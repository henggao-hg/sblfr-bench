#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(jsonlite)
  library(ragg)
  library(svglite)
  library(scales)
  library(ggrepel)
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
arm_labels <- c(
  single = "A1\nSingle",
  actor_rubric = "A2\nActor\nrubric",
  free_critic = "A3\nFree\ncritic",
  thin_critic = "A4\nThin\ncritic",
  bo3 = "A9\nBest-of-3",
  sc3_vote = "A5\nSC-3\nvote",
  sc3_agg = "A6\nSC-3\nagg.",
  team_vote = "A7\nTeam\nvote",
  team_agg = "A8\nTeam\nagg."
)
arm_code <- c(
  single = "A1", actor_rubric = "A2", free_critic = "A3", thin_critic = "A4",
  bo3 = "A9", sc3_vote = "A5", sc3_agg = "A6", team_vote = "A7", team_agg = "A8"
)

family_class_levels <- c(
  "f1_no_fault", "f1_top_up_feasible", "f1_dilute_feasible", "f1_rebuild_needed",
  "f2_no_fault", "f2_instrument_recalibrate", "f2_chemistry_recoverable", "f2_chemistry_rebuild",
  "f3_no_fault", "f3_rebalance_feasible", "f3_rebalance_rebuild"
)
family_class_labels <- c(
  f1_no_fault = "F1 no fault",
  f1_top_up_feasible = "F1 top-up",
  f1_dilute_feasible = "F1 dilute",
  f1_rebuild_needed = "F1 rebuild",
  f2_no_fault = "F2 no fault",
  f2_instrument_recalibrate = "F2 instrument",
  f2_chemistry_recoverable = "F2 chemistry\nrecoverable",
  f2_chemistry_rebuild = "F2 rebuild",
  f3_no_fault = "F3 no fault",
  f3_rebalance_feasible = "F3 rebalance\nfeasible",
  f3_rebalance_rebuild = "F3 rebuild"
)

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

theme_paper <- function(base_size = 8) {
  theme_classic(base_size = base_size) +
    theme(
      axis.line = element_line(linewidth = 0.3, color = "black"),
      axis.ticks = element_line(linewidth = 0.3, color = "black"),
      axis.text = element_text(color = "black"),
      strip.background = element_blank(),
      strip.text = element_text(face = "bold", hjust = 0, color = "black"),
      legend.position = "top",
      legend.title = element_blank(),
      legend.key.size = unit(0.38, "cm"),
      panel.spacing = unit(0.42, "cm"),
      plot.margin = margin(4, 4, 4, 4)
    )
}

rates <- dat |>
  group_by(model_group, arm) |>
  summarise(
    n = n(),
    success = mean(outcome == "SUCCESS"),
    cf = mean(outcome == "CRITICAL_FAIL"),
    over = mean(outcome == "OVER_CONSERVATIVE"),
    unmanaged = mean(outcome == "UNMANAGED"),
    .groups = "drop"
  ) |>
  mutate(
    arm = factor(arm, levels = arm_levels),
    arm_code = arm_code[as.character(arm)]
  )

# Panel-style outcome distribution: muted palette, no figure title.
outcome_levels <- c("UNMANAGED", "OVER_CONSERVATIVE", "CRITICAL_FAIL", "SUCCESS")
outcome_df <- dat |>
  mutate(
    arm = factor(arm, levels = arm_levels),
    outcome = factor(outcome, levels = outcome_levels)
  ) |>
  count(model_group, arm, outcome, name = "n") |>
  group_by(model_group, arm) |>
  mutate(frac = n / sum(n)) |>
  ungroup()

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

p_outcome <- ggplot(outcome_df, aes(x = arm, y = frac, fill = outcome)) +
  geom_col(width = 0.72, color = "white", linewidth = 0.2) +
  facet_wrap(~ model_group, ncol = 1) +
  scale_x_discrete(labels = arm_labels) +
  scale_y_continuous(labels = percent_format(accuracy = 1), expand = c(0, 0)) +
  scale_fill_manual(
    values = outcome_cols,
    breaks = rev(outcome_levels),
    labels = outcome_labs[rev(outcome_levels)]
  ) +
  coord_cartesian(ylim = c(0, 1), clip = "off") +
  labs(x = NULL, y = "Episodes (%)") +
  theme_paper(8) +
  theme(
    axis.text.x = element_text(size = 6.2, lineheight = 0.85),
    panel.grid.major.y = element_line(color = "#e6e6e6", linewidth = 0.25)
  )
save_plot(p_outcome, "paper_seed0_outcome_stacked", 7.1, 4.5)

# Trade-off: no long labels; arm codes label the points.
p_trade <- ggplot(rates, aes(x = 100 * success, y = 100 * cf)) +
  geom_point(shape = 21, size = 2.3, stroke = 0.35, fill = "white", color = "black") +
  ggrepel::geom_text_repel(
    aes(label = arm_code),
    size = 2.35,
    min.segment.length = 0,
    segment.size = 0.18,
    segment.color = "#666666",
    box.padding = 0.25,
    point.padding = 0.55,
    max.overlaps = Inf,
    force = 18
  ) +
  facet_wrap(~ model_group, ncol = 1, scales = "free_x") +
  scale_x_continuous(labels = function(x) paste0(round(x), "%"), expand = expansion(mult = 0.08)) +
  scale_y_continuous(labels = function(x) paste0(round(x), "%"), expand = expansion(mult = 0.08)) +
  labs(x = "Success rate", y = "Critical-fail rate") +
  theme_paper(8) +
  theme(panel.grid.major = element_line(color = "#eeeeee", linewidth = 0.25))
save_plot(p_trade, "paper_seed0_success_cf_tradeoff", 5.3, 4.4)

# Class heatmap: one hue, no figure title.
heat_df <- dat |>
  mutate(
    arm = factor(arm, levels = arm_levels),
    family_class = factor(paste(family, class, sep = "_"), levels = family_class_levels)
  ) |>
  group_by(model_group, family_class, arm) |>
  summarise(success_pct = 100 * mean(outcome == "SUCCESS"), .groups = "drop")

p_heat <- ggplot(heat_df, aes(x = arm, y = family_class, fill = success_pct)) +
  geom_tile(color = "white", linewidth = 0.18) +
  facet_wrap(~ model_group, ncol = 1) +
  scale_x_discrete(labels = arm_labels) +
  scale_y_discrete(labels = family_class_labels) +
  scale_fill_gradient(low = "#f7f7f7", high = "#2f6b3a", limits = c(0, 100), labels = function(x) paste0(x, "%")) +
  labs(x = NULL, y = NULL, fill = "Success") +
  theme_paper(7.3) +
  theme(
    axis.text.x = element_text(size = 5.8, lineheight = 0.84),
    axis.text.y = element_text(size = 6.4),
    axis.line = element_blank(),
    axis.ticks = element_blank(),
    legend.position = "right"
  )
save_plot(p_heat, "paper_seed0_success_by_class_heatmap", 7.2, 5.4)

# C1-C6 contrasts: small, muted, with no in-plot essay.
safe_classes <- c("instrument_recalibrate", "rebuild_needed", "chemistry_rebuild", "rebalance_rebuild")
rate_by <- function(df) {
  df |>
    group_by(model_group, arm) |>
    summarise(success = mean(outcome == "SUCCESS"), cf = mean(outcome == "CRITICAL_FAIL"), .groups = "drop")
}
rates_all <- rate_by(dat)
rates_safe <- rate_by(dat |> filter(class %in% safe_classes))
contrast_specs <- tibble::tribble(
  ~contrast, ~arm_a, ~arm_b, ~subset_name,
  "C1", "single", "actor_rubric", "all",
  "C2", "single", "free_critic", "all",
  "C3", "free_critic", "thin_critic", "all",
  "C4 vote", "sc3_vote", "team_vote", "all",
  "C4 agg.", "sc3_agg", "team_agg", "all",
  "C5", "single", "bo3", "all",
  "C6", "single", "thin_critic", "safety"
)
lookup <- function(model, arm_id, subset_name) {
  src <- if (subset_name == "safety") rates_safe else rates_all
  src |> filter(.data$model_group == .env$model, .data$arm == .env$arm_id)
}
contrast_df <- bind_rows(lapply(unique(dat$model_group), function(model) {
  bind_rows(lapply(seq_len(nrow(contrast_specs)), function(i) {
    s <- contrast_specs[i, ]
    a <- lookup(model, s$arm_a[[1]], s$subset_name[[1]])
    b <- lookup(model, s$arm_b[[1]], s$subset_name[[1]])
    tibble(
      model_group = model,
      contrast = s$contrast[[1]],
      success_delta = 100 * (b$success - a$success),
      cf_delta = 100 * (b$cf - a$cf)
    )
  }))
}))
contrast_long <- bind_rows(
  contrast_df |> transmute(model_group, contrast, metric = "Success gain", delta = success_delta),
  contrast_df |> transmute(model_group, contrast, metric = "Critical-fail reduction", delta = -cf_delta)
) |>
  mutate(
    contrast = factor(contrast, levels = rev(unique(contrast_specs$contrast))),
    metric = factor(metric, levels = c("Success gain", "Critical-fail reduction"))
  )

p_contrast <- ggplot(contrast_long, aes(x = delta, y = contrast, fill = metric)) +
  geom_vline(xintercept = 0, color = "#666666", linewidth = 0.25) +
  geom_col(position = position_dodge(width = 0.65), width = 0.52) +
  facet_wrap(~ model_group, ncol = 1) +
  scale_x_continuous(labels = function(x) paste0(ifelse(x > 0, "+", ""), round(x), " pp")) +
  scale_fill_manual(values = c(`Success gain` = "#2f6b3a", `Critical-fail reduction` = "#5B6E9E")) +
  labs(x = "Improvement", y = NULL) +
  theme_paper(8) +
  theme(panel.grid.major.x = element_line(color = "#eeeeee", linewidth = 0.25))
save_plot(p_contrast, "paper_seed0_C1_C6_contrasts", 5.8, 4.5)
