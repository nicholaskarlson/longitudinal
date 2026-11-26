## Independent base-R route for the public ordinary anchor. No packages required.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 1L) stop("usage: Rscript examples/base_r.R OUTPUT.tsv")
data_dir <- file.path("data", "anchor")
read <- function(name) read.csv(file.path(data_dir, paste0(name, ".csv")),
                                colClasses = "character", na.strings = NULL,
                                check.names = FALSE)
p <- read("participants"); b <- read("baseline")
f <- read("followup_long"); r <- read("registry")
if (nrow(p) != 1600L || nrow(b) != 1219L || nrow(f) != 3657L ||
    anyDuplicated(p$student_id) || anyDuplicated(b$student_id) ||
    anyDuplicated(r$student_id) || !setequal(b$student_id, r$student_id) ||
    !all(b$student_id %in% p$student_id)) stop("anchor keys")
if (!setequal(b$offer, c("0", "1"))) stop("invalid offer")
expected_keys <- as.vector(outer(b$student_id, c("3", "6", "12"), paste, sep = ":"))
follow_keys <- paste(f$student_id, f$wave_month, sep = ":")
if (anyDuplicated(follow_keys) || !setequal(follow_keys, expected_keys)) stop("panel keys")
ids <- b$student_id[b$offer == "0"]
result <- c(sampled_invitees = nrow(p), baseline_respondents = nrow(b),
            unoffered = length(ids))
item_score <- function(frame) {
  raw <- as.matrix(frame[, paste0("st", 1:5)])
  if (!all(raw %in% c("", as.character(1:5)))) stop("invalid item")
  present <- raw != ""
  values <- matrix(as.numeric(ifelse(present, raw, "0")), nrow = nrow(frame))
  values[,4] <- ifelse(present[,4], 6 - values[,4], 0)
  count <- rowSums(present)
  ifelse(count >= 4, rowSums(values) / pmax(count, 1), NA_real_)
}
score_matrix <- matrix(NA_real_, nrow = length(ids), ncol = 4L)
for (j in seq_along(c("0", "3", "6", "12"))) {
  month <- c("0", "3", "6", "12")[j]
  if (month == "0") {
    rows <- b[match(ids, b$student_id), , drop = FALSE]
    returned <- rep(TRUE, nrow(rows))
  } else {
    rows <- f[match(paste(ids, month, sep = ":"), follow_keys), , drop = FALSE]
    if (!all(rows$responded %in% c("0", "1"))) stop("invalid response")
    returned <- rows$responded == "1"
    if (any(!returned & rowSums(as.matrix(rows[, paste0("st", 1:5)]) != "") > 0))
      stop("unreturned items")
  }
  score_matrix[,j] <- ifelse(returned, item_score(rows), NA_real_)
  result[paste0("returned_", month)] <- sum(returned)
  result[paste0("scored_", month)] <- sum(is.finite(score_matrix[,j]))
}
complete <- score_matrix[complete.cases(score_matrix), , drop = FALSE]
result["four_scored"] <- nrow(complete)
result["paired_difference"] <- mean(complete[,4] - complete[,1])
types <- c("withdrawal", "transfer", "consent_withdrawn", "none")
if (!setequal(r$exit_type, types)) stop("invalid event")
time <- as.numeric(r$exit_month)
if (any(!is.finite(time) | time <= 0 | time > 12) ||
    any((r$exit_type == "none") != (time == 12)) ||
    any(r$withdrawn_12 != as.character(as.integer(r$exit_type == "withdrawal"))) ||
    any(r$transferred_12 != as.character(as.integer(r$exit_type == "transfer"))))
  stop("invalid time or flag")
result["withdrawals_12"] <- sum(r$exit_type == "withdrawal")
result["transfers_12"] <- sum(r$exit_type == "transfer")
result["consent_censored_12"] <- sum(r$exit_type == "consent_withdrawn")
event_free <- 1; cif_w <- 0; cif_t <- 0
for (t in sort(unique(time[r$exit_type != "none"]))) {
  risk <- sum(time >= t)
  w <- sum(time == t & r$exit_type == "withdrawal")
  tr <- sum(time == t & r$exit_type == "transfer")
  cif_w <- cif_w + event_free * w / risk
  cif_t <- cif_t + event_free * tr / risk
  event_free <- event_free * (1 - (w + tr) / risk)
}
result["event_free_12"] <- event_free
result["cif_withdrawal_12"] <- cif_w
result["cif_transfer_12"] <- cif_t
write.table(data.frame(metric = names(result), value = as.numeric(result)),
            args[1], sep = "\t", row.names = FALSE, quote = FALSE)
cat("BOOK14_PUBLIC_BASE_R_OK\n")
