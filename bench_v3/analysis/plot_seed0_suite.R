#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(jsonlite)
  library(scales)
  library(ragg)
  library(svglite)
  library(ggrepel)
})

root <- normalizePath(file.path(getwd()), mustWork = TRUE)
results_dir <- file.path(root, "bench_v3", "results")
out_dir <- file.path(root, "bench_v3", "analysis", "tier1_seed0", "figures")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

read_jsonl <- function(path) {
  jsonlite::stream_in(file(path), verbose = FALSE)
}

strong <- read_jsonl(file.path(results_dir, "v3_tier1_strong_seed0.jsonl")) |>
  mutate(model_group = "Strong actor: Qwen3.7-Max")
weak <- read_jsonl(file.path(results_dir, "v3_tier1_weak_seed0.jsonl")) |>
  mutate(model_group = "Weak actor: Qwen2.5-32B")
dat <- bind_rows(strong, weak)

arm_levels <- c(
  "single", "actor_rubric", "free_critic", "thin_critic",
  "bo3", "sc3_vote", "sc3_agg", "team_vote", "team_agg"
)
arm_labels <- c(
  single = "Single",
  actor_rubric = "Actor\nrubric",
  free_critic = "Free\ncritic",
  thin_critic = "Thin\ncritic",
  bo3 = "Best-of-3",
  sc3_vote = "SC-3\nvote",
  sc3_agg = "SC-3\nagg.",
  team_vote = "Team\nvote",
  team_agg = "Team\nagg."
)
arm_labels_inline <- c(
  single = "Single",
  actor_rubric = "Actor rubric",
  free_critic = "Free critic",
  thin_critic = "Thin critic",
  bo3 = "Best-of-3",
  sc3_vote = "SC-3 vote",
  sc3_agg = "SC-3 agg.",
  team_vote = "Team vote",
  team_agg = "Team agg."
)
arm_code <- c(
  single = "A1",
  actor_rubric = "A2",
  free_critic = "A3",
  thin_critic = "A4",
  bo3 = "A9",
  sc3_vote = "A5",
  sc3_agg = "A6",
  team_vote = "A7",
  team_agg = "A8"
)
arm_family <- c(
  single = "Single",
  actor_rubric = "Rubric",
  free_critic = "Critic",
  thin_critic = "Critic",
  bo3 = "Best-of-3",
  sc3_vote = "Sampling",
  sc3_agg = "Sampling",
  team_vote = "Team",
  team_agg = "Team"
)
family_cols <- c(
  Single = "#333333",
  Rubric = "#7B3294",
  Critic = "#1B9E77",
  `Best-of-3` = "#D95F02",
  Sampling = "#7570B3",
  Team = "#E7298A"
)
outcome_cols <- c(
  SUCCESS = "#2E7D32",
  CRITICAL_FAIL = "#B71C1C",
  OVER_CONSERVATIVE = "#F9A825",
  UNMANAGED = "#737373"
)
outcome_labels <- c(
  SUCCESS = "Success",
  CRITICAL_FAIL = "Critical fail",
  OVER_CONSERVATIVE = "Over-conservative",
  UNMANAGED = "Unmanaged"
)

family_class_levels <- c(
  "f1_no_fault",
  "f1_top_up_feasible",
  "f1_dilute_feasible",
  "f1_rebuild_needed",
  "f2_no_fault",
  "f2_instrument_recalibrate",
  "f2_chemistry_recoverable",
  "f2_chemistry_rebuild",
  "f3_no_fault",
  "f3_rebalance_feasible",
  "f3_rebalance_rebuild"
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
  ragg::agg_png(png_path, width = width, height = height, units = "in", res = 220)
  print(plot)
  dev.off()
  svglite::svglite(svg_path, width = width, height = height)
  print(plot)
  dev.off()
  cat("wrote", png_path, "\n")
  cat("wrote", svg_path, "\n")
}

theme_report <- function(base_size = 11) {
  theme_minimal(base_size = base_size) +
    theme(
      plot.title = element_text(face = "bold", size = base_size + 4),
      plot.subtitle = element_text(size = base_size - 1, color = "#444444", margin = margin(b = 8)),
      panel.grid.minor = element_blank(),
      legend.position = "top",
      legend.justification = "left",
      legend.title = element_blank(),
      strip.text = element_text(face = "bold", hjust = 0),
      strip.background = element_rect(fill = "#F3F3F3", color = NA),
      plot.margin = margin(8, 12, 8, 8)
    )
}

rate_by <- function(df, group_cols) {
  df |>
    group_by(across(all_of(group_cols))) |>
    summarise(
      n = n(),
      success = mean(outcome == "SUCCESS"),
      cf = mean(outcome == "CRITICAL_FAIL"),
      over = mean(outcome == "OVER_CONSERVATIVE"),
      unmanaged = mean(outcome == "UNMANAGED"),
      .groups = "drop"
    )
}

safe_classes <- c(
  "instrument_recalibrate",
  "rebuild_needed",
  "chemistry_rebuild",
  "rebalance_rebuild"
)

contrast_specs <- tibble::tribble(
  ~contrast, ~arm_a, ~arm_b, ~subset_name,
  "C1 Actor rubric", "single", "actor_rubric", "all",
  "C2 Free critic", "single", "free_critic", "all",
  "C3 Thin vs free", "free_critic", "thin_critic", "all",
  "C4 Team vote vs SC-3 vote", "sc3_vote", "team_vote", "all",
  "C4 Team agg. vs SC-3 agg.", "sc3_agg", "team_agg", "all",
  "C5 Best-of-3", "single", "bo3", "all",
  "C6 Thin critic on safety classes", "single", "thin_critic", "safety"
)

rates_all <- rate_by(dat, c("model_group", "arm"))
rates_safe <- dat |>
  filter(class %in% safe_classes) |>
  rate_by(c("model_group", "arm"))

lookup_rate <- function(model, arm_id, subset_name) {
  src <- if (subset_name == "safety") rates_safe else rates_all
  src |> filter(.data$model_group == .env$model, .data$arm == .env$arm_id)
}

contrast_df <- bind_rows(lapply(unique(dat$model_group), function(model) {
  bind_rows(lapply(seq_len(nrow(contrast_specs)), function(i) {
    spec <- contrast_specs[i, ]
    a <- lookup_rate(model, spec$arm_a[[1]], spec$subset_name[[1]])
    b <- lookup_rate(model, spec$arm_b[[1]], spec$subset_name[[1]])
    tibble(
      model_group = model,
      contrast = spec$contrast[[1]],
      subset_name = spec$subset_name[[1]],
      success_delta = 100 * (b$success - a$success),
      cf_delta = 100 * (b$cf - a$cf)
    )
  }))
}))

contrast_df <- contrast_df |>
  mutate(
    contrast = factor(contrast, levels = rev(unique(contrast_specs$contrast))),
    metric = "Success"
  )

contrast_long <- bind_rows(
  contrast_df |> transmute(model_group, contrast, metric = "Success gain", delta = success_delta),
  contrast_df |> transmute(model_group, contrast, metric = "Critical-fail reduction", delta = -cf_delta)
) |>
  mutate(metric = factor(metric, levels = c("Success gain", "Critical-fail reduction")))

p_contrast <- ggplot(contrast_long, aes(x = delta, y = contrast, fill = metric)) +
  geom_vline(xintercept = 0, color = "#777777", linewidth = 0.35) +
  geom_col(position = position_dodge(width = 0.68), width = 0.58) +
  facet_wrap(~ model_group, ncol = 1) +
  scale_x_continuous(labels = function(x) paste0(ifelse(x > 0, "+", ""), round(x), " pp")) +
  scale_fill_manual(values = c(`Success gain` = "#2E7D32", `Critical-fail reduction` = "#5B6E9E")) +
  labs(
    title = "C1-C6 improvements",
    subtitle = "Each row uses its own pre-registered baseline. Positive values are better for both metrics.",
    x = "Improvement relative to that contrast's baseline",
    y = NULL
  ) +
  theme_report(10) +
  theme(
    axis.text.y = element_text(size = 8.5),
    panel.grid.major.y = element_blank()
  )
save_plot(p_contrast, "seed0_C1_C6_contrasts", 9.5, 6.2)

tradeoff_df <- rates_all |>
  mutate(
    arm = factor(arm, levels = arm_levels),
    arm_label = arm_labels_inline[as.character(arm)],
    arm_code = arm_code[as.character(arm)],
    family = factor(arm_family[as.character(arm)], levels = names(family_cols)),
    success_pct = 100 * success,
    cf_pct = 100 * cf
  )

p_tradeoff <- ggplot(tradeoff_df, aes(x = success_pct, y = cf_pct, color = family, label = arm_label)) +
  geom_point(shape = 21, size = 3.0, stroke = 0.45, fill = "white", alpha = 0.95) +
  ggrepel::geom_text_repel(
    aes(label = arm_code),
    size = 3.0,
    min.segment.length = 0,
    segment.size = 0.22,
    segment.color = "#666666",
    box.padding = 0.45,
    point.padding = 0.42,
    max.overlaps = Inf,
    force = 18,
    show.legend = FALSE
  ) +
  facet_wrap(~ model_group, ncol = 1, scales = "free_x") +
  scale_color_manual(values = family_cols) +
  scale_x_continuous(labels = function(x) paste0(round(x), "%")) +
  scale_y_continuous(labels = function(x) paste0(round(x), "%")) +
  labs(
    title = "Success and critical-failure trade-off",
    subtitle = "Each point is one agent configuration over 275 matched seed0 episodes.",
    x = "Success rate",
    y = "Critical-fail rate"
  ) +
  theme_report(10) +
  theme(panel.grid.minor = element_blank())
save_plot(p_tradeoff, "seed0_success_cf_tradeoff", 8.6, 6.2)

heat_df <- dat |>
  mutate(
    arm = factor(arm, levels = arm_levels),
    family_class = factor(paste(family, class, sep = "_"), levels = family_class_levels)
  ) |>
  group_by(model_group, family_class, arm) |>
  summarise(success_pct = 100 * mean(outcome == "SUCCESS"), .groups = "drop")

p_heat <- ggplot(heat_df, aes(x = arm, y = family_class, fill = success_pct)) +
  geom_tile(color = "white", linewidth = 0.25) +
  facet_wrap(~ model_group, ncol = 1) +
  scale_x_discrete(labels = arm_labels) +
  scale_y_discrete(labels = family_class_labels) +
  scale_fill_gradient(low = "#F7FBFF", high = "#1B7837", limits = c(0, 100), labels = function(x) paste0(x, "%")) +
  labs(
    title = "Where each configuration succeeds",
    subtitle = "Success rate by family-qualified fault class. Each cell summarizes 25 episodes.",
    x = NULL,
    y = NULL,
    fill = "Success"
  ) +
  theme_report(9.5) +
  theme(
    axis.text.x = element_text(size = 7.7, lineheight = 0.9),
    axis.text.y = element_text(size = 8.2),
    panel.grid = element_blank(),
    legend.position = "right"
  )
save_plot(p_heat, "seed0_success_by_class_heatmap", 9.5, 7.2)

action_group <- c(
  measure_concentration = "Measure batch",
  measure_volume = "Measure batch",
  measure_stock_volume = "Measure batch",
  measure_stock_concentration = "Measure batch",
  measure_standard_concentration = "Verify anchor",
  recalibrate = "Calibrate",
  transfer = "Correct in place",
  dilute_to = "Correct in place",
  discard_vessel = "Rebuild/isolate",
  quarantine_stock = "Rebuild/isolate",
  accept_batch = "Terminal",
  abort_and_handoff = "Terminal"
)
group_levels <- c("Measure batch", "Verify anchor", "Calibrate", "Correct in place", "Rebuild/isolate", "Terminal")

rows_to_action_counts <- function(df) {
  out <- vector("list", nrow(df))
  for (i in seq_len(nrow(df))) {
    types <- df$committed_types[[i]]
    if (length(types) == 0) next
    groups <- unname(action_group[types])
    groups <- groups[!is.na(groups)]
    if (length(groups) == 0) next
    out[[i]] <- tibble(
      model_group = df$model_group[[i]],
      arm = df$arm[[i]],
      group = groups
    )
  }
  bind_rows(out)
}

action_steps <- rows_to_action_counts(dat)
share_df <- action_steps |>
  count(model_group, arm, group, name = "n") |>
  group_by(model_group, arm) |>
  mutate(share = n / sum(n)) |>
  ungroup() |>
  mutate(
    arm = factor(arm, levels = arm_levels),
    group = factor(group, levels = group_levels)
  )

p_action_share <- ggplot(share_df, aes(x = arm, y = share, fill = group)) +
  geom_col(width = 0.72, color = "white", linewidth = 0.2) +
  facet_wrap(~ model_group, ncol = 1) +
  scale_x_discrete(labels = arm_labels) +
  scale_y_continuous(labels = percent_format(accuracy = 1), expand = c(0, 0)) +
  scale_fill_manual(values = c(
    "Measure batch" = "#4C78A8",
    "Verify anchor" = "#72B7B2",
    "Calibrate" = "#F58518",
    "Correct in place" = "#54A24B",
    "Rebuild/isolate" = "#B279A2",
    "Terminal" = "#777777"
  )) +
  labs(
    title = "Action mix by agent configuration",
    subtitle = "Step-weighted distribution of committed action types. This is a mechanism view, not a success metric.",
    x = NULL,
    y = "Committed actions",
    fill = NULL
  ) +
  coord_cartesian(ylim = c(0, 1), clip = "off") +
  theme_report(10) +
  theme(
    axis.text.x = element_text(size = 8, lineheight = 0.9),
    panel.grid.major.x = element_blank()
  )
save_plot(p_action_share, "seed0_action_mix_stacked", 9.5, 6.4)

make_group_share <- function(df) {
  steps <- rows_to_action_counts(df)
  counts <- table(factor(steps$group, levels = group_levels))
  as.numeric(counts) / max(1, sum(counts))
}
jsd_vec <- function(p, q) {
  m <- (p + q) / 2
  kl <- function(a) {
    idx <- a > 0 & m > 0
    sum(a[idx] * log2(a[idx] / m[idx]))
  }
  0.5 * kl(p) + 0.5 * kl(q)
}

jsd_df <- bind_rows(lapply(unique(dat$model_group), function(model) {
  model_dat <- dat |> filter(model_group == model)
  single_p <- make_group_share(model_dat |> filter(arm == "single"))
  bind_rows(lapply(setdiff(arm_levels, "single"), function(a) {
    p <- make_group_share(model_dat |> filter(arm == a))
    tibble(model_group = model, arm = a, jsd = jsd_vec(p, single_p))
  }))
})) |>
  mutate(
    arm = factor(arm, levels = arm_levels)
  )

p_jsd <- ggplot(jsd_df, aes(x = arm, y = jsd)) +
  geom_col(width = 0.7, fill = "#6f6f6f") +
  facet_wrap(~ model_group, ncol = 1, scales = "free_y") +
  scale_x_discrete(labels = arm_labels) +
  labs(
    title = "Action-distribution shift from single agent",
    subtitle = "Jensen-Shannon divergence. Larger values mean different behavior, not necessarily better behavior.",
    x = NULL,
    y = "JSD vs single"
  ) +
  theme_report(10) +
  theme(
    axis.text.x = element_text(size = 8, lineheight = 0.9),
    panel.grid.major.x = element_blank(),
    legend.position = "none"
  )
save_plot(p_jsd, "seed0_jsd_vs_single", 8.8, 5.6)
