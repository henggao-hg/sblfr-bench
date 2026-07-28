#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(jsonlite)
  library(patchwork)
  library(ragg)
  library(svglite)
  library(scales)
})

root <- normalizePath(file.path(getwd()), mustWork = TRUE)
results_dir <- file.path(root, "bench_v3", "results")
out_dir <- file.path(root, "bench_v3", "analysis", "tier1_seed0", "figures")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

read_jsonl <- function(path) jsonlite::stream_in(file(path), verbose = FALSE)

dat <- bind_rows(
  read_jsonl(file.path(results_dir, "v3_tier1_strong_seed0.jsonl")) |>
    mutate(model_group = "Strong actor"),
  read_jsonl(file.path(results_dir, "v3_tier1_weak_seed0.jsonl")) |>
    mutate(model_group = "Weak actor")
)

arm_levels <- c(
  "single", "actor_rubric", "free_critic", "thin_critic",
  "bo3", "sc3_vote", "sc3_agg", "team_vote", "team_agg"
)
arm_code <- c(
  single = "A1", actor_rubric = "A2", free_critic = "A3", thin_critic = "A4",
  bo3 = "A9", sc3_vote = "A5", sc3_agg = "A6", team_vote = "A7", team_agg = "A8"
)
arm_codes_non_single <- arm_code[setdiff(arm_levels, "single")]

theme_comp <- function(base_size = 7.5) {
  theme_classic(base_size = base_size) +
    theme(
      axis.line = element_line(linewidth = 0.25, color = "black"),
      axis.ticks = element_line(linewidth = 0.25, color = "black"),
      axis.text = element_text(color = "black"),
      strip.background = element_blank(),
      strip.text = element_text(face = "bold", hjust = 0, color = "black"),
      legend.position = "top",
      legend.title = element_blank(),
      legend.key.size = unit(0.32, "cm"),
      legend.text = element_text(size = rel(0.9)),
      panel.spacing = unit(0.32, "cm"),
      plot.margin = margin(3, 3, 3, 3)
    )
}

save_plot <- function(plot, name, width, height) {
  png_path <- file.path(out_dir, paste0(name, ".png"))
  svg_path <- file.path(out_dir, paste0(name, ".svg"))
  ragg::agg_png(png_path, width = width, height = height, units = "in", res = 300)
  print(plot)
  dev.off()
  svglite::svglite(svg_path, width = width, height = height)
  print(plot)
  dev.off()
  cat("wrote", png_path, "\n")
  cat("wrote", svg_path, "\n")
}

# a. Framework schematic. The panel is intentionally schematic-only; scoring is not shown.
box_df <- tibble::tribble(
  ~id, ~x, ~y, ~w, ~h, ~label,
  "obs",      0.14, 0.58, 0.22, 0.18, "Visible state\n+ action log",
  "recovery", 0.38, 0.58, 0.20, 0.18, "Recovery\nagent(s)",
  "review",   0.61, 0.58, 0.22, 0.18, "Critic /\naggregator",
  "verify",   0.84, 0.58, 0.20, 0.18, "Verifier +\nsimulator"
)

arrow_df <- tibble::tribble(
  ~x, ~y, ~xend, ~yend,
  0.25, 0.58, 0.29, 0.58,
  0.48, 0.58, 0.51, 0.58,
  0.72, 0.58, 0.76, 0.58,
  0.84, 0.44, 0.14, 0.44,
  0.14, 0.44, 0.14, 0.49
)

p_framework <- ggplot() +
  geom_rect(
    data = box_df,
    aes(xmin = x - w / 2, xmax = x + w / 2, ymin = y - h / 2, ymax = y + h / 2),
    fill = "#f7f7f7", color = "black", linewidth = 0.25
  ) +
  geom_segment(
    data = arrow_df,
    aes(x = x, y = y, xend = xend, yend = yend),
    linewidth = 0.28,
    arrow = arrow(length = unit(0.085, "in"), type = "closed")
  ) +
  geom_text(data = box_df, aes(x = x, y = y, label = label), size = 2.55, lineheight = 0.9) +
  annotate("text", x = 0.385, y = 0.70, label = "propose", size = 2.0, hjust = 0.5) +
  annotate("text", x = 0.615, y = 0.70, label = "review / select", size = 2.0, hjust = 0.5) +
  annotate("text", x = 0.49, y = 0.39, label = "feedback", size = 2.0, hjust = 0.5) +
  coord_cartesian(xlim = c(0, 1), ylim = c(0.32, 0.78), clip = "off") +
  theme_void(base_size = 7.5) +
  theme(plot.margin = margin(2, 2, 2, 2))

# b. Main outcome by arm.
outcome_levels <- c("UNMANAGED", "OVER_CONSERVATIVE", "CRITICAL_FAIL", "SUCCESS")
outcome_cols <- c(
  SUCCESS = "#2f6b3a",
  CRITICAL_FAIL = "#9e3b3b",
  OVER_CONSERVATIVE = "#bdbdbd",
  UNMANAGED = "#eeeeee"
)
outcome_labs <- c(
  SUCCESS = "Success",
  CRITICAL_FAIL = "Critical fail",
  OVER_CONSERVATIVE = "Over-conservative",
  UNMANAGED = "Unmanaged"
)

outcome_df <- dat |>
  mutate(
    arm = factor(arm, levels = arm_levels),
    outcome = factor(outcome, levels = outcome_levels)
  ) |>
  count(model_group, arm, outcome, name = "n") |>
  group_by(model_group, arm) |>
  mutate(frac = n / sum(n)) |>
  ungroup()

p_outcome <- ggplot(outcome_df, aes(x = arm, y = frac, fill = outcome)) +
  geom_col(width = 0.72, color = "white", linewidth = 0.18) +
  facet_wrap(~ model_group, ncol = 1) +
  scale_x_discrete(labels = arm_code) +
  scale_y_continuous(labels = percent_format(accuracy = 1), expand = c(0, 0), limits = c(0, 1)) +
  scale_fill_manual(values = outcome_cols, labels = outcome_labs, breaks = rev(outcome_levels)) +
  labs(x = NULL, y = "Episodes") +
  theme_comp(7.2) +
  theme(
    legend.position = "top",
    axis.text.x = element_text(size = 7),
    panel.grid.major.y = element_line(color = "#eeeeee", linewidth = 0.25)
  )

# c. Outcome changes relative to the single-agent arm.
rate_df <- dat |>
  group_by(model_group, arm) |>
  summarise(
    success = mean(outcome == "SUCCESS"),
    critical_fail = mean(outcome == "CRITICAL_FAIL"),
    .groups = "drop"
  )
base_df <- rate_df |>
  filter(arm == "single") |>
  select(model_group, base_success = success, base_cf = critical_fail)

delta_df <- rate_df |>
  filter(arm != "single") |>
  left_join(base_df, by = "model_group") |>
  transmute(
    model_group,
    arm = factor(arm, levels = setdiff(arm_levels, "single")),
    `Success gain` = 100 * (success - base_success),
    `Critical-fail reduction` = 100 * (base_cf - critical_fail)
  ) |>
  tidyr::pivot_longer(cols = c(`Success gain`, `Critical-fail reduction`), names_to = "metric", values_to = "delta") |>
  mutate(metric = factor(metric, levels = c("Success gain", "Critical-fail reduction")))

p_delta <- ggplot(delta_df, aes(x = arm, y = delta, fill = metric)) +
  geom_hline(yintercept = 0, color = "black", linewidth = 0.25) +
  geom_col(position = position_dodge(width = 0.62), width = 0.54) +
  facet_wrap(~ model_group, ncol = 1) +
  scale_x_discrete(labels = arm_codes_non_single) +
  scale_fill_manual(values = c(`Success gain` = "#2f6b3a", `Critical-fail reduction` = "#5B6E9E")) +
  labs(x = NULL, y = "Change vs A1 (pp)") +
  theme_comp(7.2) +
  theme(
    axis.text.x = element_text(size = 7),
    panel.grid.major.y = element_line(color = "#eeeeee", linewidth = 0.25)
  )

# d. Action-distribution shift by JSD.
action_groups <- list(
  measure = c("measure_concentration", "measure_volume", "measure_standard_concentration", "measure_stock_concentration"),
  calibrate = c("recalibrate_instrument"),
  correct = c("transfer", "dilute_to"),
  rebuild = c("discard_vessel"),
  terminate = c("accept_batch", "abort_and_handoff"),
  quarantine = c("quarantine_stock")
)
action_group <- function(action_type) {
  hit <- names(Filter(function(v) action_type %in% v, action_groups))
  if (length(hit) == 0) "other" else hit[[1]]
}
make_group_share <- function(rows) {
  types <- unlist(rows$committed_types, use.names = FALSE)
  groups <- vapply(types, action_group, character(1))
  tab <- table(factor(groups, levels = names(action_groups)))
  as.numeric(tab) / max(sum(tab), 1)
}
jsd_vec <- function(p, q) {
  m <- 0.5 * (p + q)
  kl <- function(a, b) sum(ifelse(a > 0, a * log2(a / b), 0))
  0.5 * kl(p, m) + 0.5 * kl(q, m)
}

jsd_df <- bind_rows(lapply(unique(dat$model_group), function(model) {
  model_dat <- dat |> filter(model_group == model)
  single_p <- make_group_share(model_dat |> filter(arm == "single"))
  bind_rows(lapply(setdiff(arm_levels, "single"), function(a) {
    p <- make_group_share(model_dat |> filter(arm == a))
    tibble(model_group = model, arm = a, jsd = jsd_vec(p, single_p))
  }))
})) |>
  mutate(arm = factor(arm, levels = setdiff(arm_levels, "single")))

p_jsd <- ggplot(jsd_df, aes(x = arm, y = jsd)) +
  geom_col(width = 0.7, fill = "#707070") +
  facet_wrap(~ model_group, ncol = 1, scales = "free_y") +
  scale_x_discrete(labels = arm_codes_non_single) +
  labs(x = NULL, y = "JSD from A1") +
  theme_comp(7.2) +
  theme(
    legend.position = "none",
    axis.text.x = element_text(size = 7),
    panel.grid.major.y = element_line(color = "#eeeeee", linewidth = 0.25)
  )

layout <- "
AAABBB
AAABBB
CCCDDD
CCCDDD
"

composite <- p_framework + p_outcome + p_delta + p_jsd +
  plot_layout(design = layout) +
  plot_annotation(tag_levels = "a") &
  theme(
    plot.tag = element_text(face = "bold", size = 10),
    plot.tag.position = c(0.01, 0.99)
  )

save_plot(composite, "paper_seed0_composite", 7.4, 6.4)
