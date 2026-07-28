#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(jsonlite)
  library(scales)
  library(ragg)
  library(svglite)
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
outcome_levels <- c("UNMANAGED", "OVER_CONSERVATIVE", "CRITICAL_FAIL", "SUCCESS")
outcome_labels <- c(
  SUCCESS = "Success",
  CRITICAL_FAIL = "Critical fail",
  OVER_CONSERVATIVE = "Over-conservative",
  UNMANAGED = "Unmanaged"
)
outcome_cols <- c(
  SUCCESS = "#2E7D32",
  CRITICAL_FAIL = "#B71C1C",
  OVER_CONSERVATIVE = "#F9A825",
  UNMANAGED = "#737373"
)

plot_df <- bind_rows(strong, weak) |>
  mutate(
    arm = factor(arm, levels = arm_levels),
    outcome = factor(outcome, levels = outcome_levels)
  ) |>
  count(model_group, arm, outcome, name = "n") |>
  group_by(model_group, arm) |>
  mutate(frac = n / sum(n)) |>
  ungroup()

p <- ggplot(plot_df, aes(x = arm, y = frac, fill = outcome)) +
  geom_col(width = 0.72, color = "white", linewidth = 0.25) +
  facet_wrap(~ model_group, ncol = 1) +
  scale_x_discrete(labels = arm_labels) +
  scale_y_continuous(labels = percent_format(accuracy = 1), expand = c(0, 0)) +
  scale_fill_manual(
    values = outcome_cols,
    breaks = rev(outcome_levels),
    labels = outcome_labels[rev(outcome_levels)]
  ) +
  labs(
    title = "Tier-1 seed0 outcomes by agent configuration",
    subtitle = "Each bar summarizes 275 matched episodes. Strong and weak actors use the same instances and arms.",
    x = NULL,
    y = "Episodes",
    fill = NULL
  ) +
  coord_cartesian(ylim = c(0, 1), clip = "off") +
  theme_minimal(base_size = 11) +
  theme(
    plot.title = element_text(face = "bold", size = 15),
    plot.subtitle = element_text(size = 10, color = "#444444", margin = margin(b = 8)),
    axis.text.x = element_text(size = 8.5, lineheight = 0.9),
    axis.text.y = element_text(size = 9),
    panel.grid.major.x = element_blank(),
    panel.grid.minor = element_blank(),
    strip.text = element_text(face = "bold", size = 11, hjust = 0),
    strip.background = element_rect(fill = "#F3F3F3", color = NA),
    legend.position = "top",
    legend.justification = "left",
    legend.text = element_text(size = 9),
    plot.margin = margin(8, 12, 8, 8)
  )

png_path <- file.path(out_dir, "seed0_outcome_stacked.png")
svg_path <- file.path(out_dir, "seed0_outcome_stacked.svg")

ragg::agg_png(png_path, width = 9.5, height = 6.4, units = "in", res = 220)
print(p)
dev.off()

svglite::svglite(svg_path, width = 9.5, height = 6.4)
print(p)
dev.off()

cat("wrote", png_path, "\n")
cat("wrote", svg_path, "\n")
