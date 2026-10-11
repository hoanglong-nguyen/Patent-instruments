# ============================================================
# Figures 1-3 — revision R2. Based on the researcher's script; changes tagged [R2-#].
#   [R2-16] the shaded band is the cross-country RANGE (minimum to maximum) in each
#           region-year; this is now stated in the captions (see notes at the end).
#   [R2-17] figures use the ESTIMATION sample (analysis.dta: 43 countries, 2000-2023)
#           instead of all African/Asian countries in ready.dta, so that the figures
#           and the text describe the same countries as the regressions.
# ============================================================
rm(list = ls())

library(tidyverse)
library(haven)       # to read .dta files
library(patchwork)   # for combining panels in Figure 3
library(scales)      # for axis formatting
library(ggrepel)     # [R2-17] geom_text_repel() in Figure 3 needs this package

# [R2-17] estimation sample written by do_10.6.do (adjust the path)
df <- read_dta("D:/Ère de FTU (2020 - 2025)/JIEM (2023 - 2024)/cô Thúy Anh/250701_ED_review/5th submission/data/analysis.dta")

df <- df %>%
  # [R2-17] analysis.dta names the footprint `ef` (ready.dta used `eft`); country names are
  #         not stored in analysis.dta, so they are added from the ISO code
  mutate(eft = ef,
         country_name = countrycode::countrycode(country_3d, "iso3c", "country.name")) %>%
  select(country_3d, country_name, year, continent_2d, gdp, eft, cap, bio, hci) %>%
  filter(continent_2d %in% c("AF", "AS")) %>%
  mutate(continent_2d = case_match(continent_2d,
                                   "AF" ~ "Africa",
                                   "AS" ~ "Asia"
  ))

# ============================================================
# Aggregate to region-year: mean + range (min/max) for the band
# ============================================================
region_avg <- df %>%
  group_by(continent_2d, year) %>%
  summarise(
    EF_mean  = mean(eft, na.rm = TRUE),
    EF_min   = min(eft, na.rm = TRUE),
    EF_max   = max(eft, na.rm = TRUE),
    GDP_mean = mean(gdp, na.rm = TRUE),
    GDP_min  = min(gdp, na.rm = TRUE),
    GDP_max  = max(gdp, na.rm = TRUE),
    .groups = "drop"
  )

# [R2-16/17] values quoted in Section 4.1 (first and last year, estimation sample)
print(region_avg %>% filter(year %in% c(2000, 2023)) %>% select(continent_2d, year, GDP_mean, EF_mean))

# ============================================================
# Figure 1: Ecological Footprint per capita, 2000–2023, by region
# ============================================================
fig1 <- ggplot(region_avg, aes(x = year, y = EF_mean, color = continent_2d, fill = continent_2d)) +
  geom_ribbon(aes(ymin = EF_min, ymax = EF_max), alpha = 0.15, color = NA) +
  geom_line(linewidth = 1) +
  geom_point(size = 1.5) +
  scale_color_manual(values = c("Africa" = "#D55E00", "Asia" = "#0072B2")) +
  scale_fill_manual(values = c("Africa" = "#D55E00", "Asia" = "#0072B2")) +
  scale_x_continuous(breaks = seq(2000, 2023, by = 4)) +
  labs(
    x = "Year",
    y = "Ecological Footprint per capita (global hectares)",
    color = "Region",
    fill = "Region",
    caption = "Lines: cross-country mean. Shaded band: range (minimum to maximum) across countries."  # [R2-16]
  ) +
  theme_minimal(base_size = 12) +
  theme(legend.position = "bottom", panel.grid.minor = element_blank())

fig1
ggsave("figure1_ecological_footprint.png", fig1, width = 8, height = 5, dpi = 300)

# ============================================================
# Figure 2: GDP per capita, 2000–2023, by region
# ============================================================
fig2 <- ggplot(region_avg, aes(x = year, y = GDP_mean, color = continent_2d, fill = continent_2d)) +
  geom_ribbon(aes(ymin = GDP_min, ymax = GDP_max), alpha = 0.15, color = NA) +
  geom_line(linewidth = 1) +
  geom_point(size = 1.5) +
  scale_color_manual(values = c("Africa" = "#D55E00", "Asia" = "#0072B2")) +
  scale_fill_manual(values = c("Africa" = "#D55E00", "Asia" = "#0072B2")) +
  scale_x_continuous(breaks = seq(2000, 2023, by = 4)) +
  scale_y_continuous(labels = comma) +
  labs(
    x = "Year",
    y = "GDP per capita (constant 2015 US$)",
    color = "Region",
    fill = "Region",
    caption = "Lines: cross-country mean. Shaded band: range (minimum to maximum) across countries."  # [R2-16]
  ) +
  theme_minimal(base_size = 12) +
  theme(legend.position = "bottom", panel.grid.minor = element_blank())

fig2
ggsave("figure2_gdp_per_capita.png", fig2, width = 8, height = 5, dpi = 300)

# ============================================================
# Figure 3: Boxplot with the three highest countries per region labelled
# ============================================================

country_avg <- df %>%
  group_by(continent_2d, country_3d, country_name) %>%
  summarise(
    gdp_avg = mean(gdp, na.rm = TRUE),
    ef_avg  = mean(eft, na.rm = TRUE),
    .groups = "drop"
  )
# [R2-17] continent_2d is already recoded to "Africa"/"Asia" above, so the second recode is dropped

# top-3 per region rule. [R2-16] These are labels for the three highest country averages,
# not statistical outliers; the caption says so.
country_avg <- country_avg %>%
  group_by(continent_2d) %>%
  mutate(
    gdp_outlier = rank(-gdp_avg) <= 3,
    ef_outlier  = rank(-ef_avg) <= 3
  ) %>%
  ungroup()

fig3a <- ggplot(country_avg, aes(x = continent_2d, y = gdp_avg, fill = continent_2d)) +
  geom_boxplot(outlier.shape = NA, alpha = 0.5, width = 0.5) +
  geom_jitter(width = 0.08, size = 1.5, alpha = 0.5, color = "grey30") +
  geom_text_repel(
    data = filter(country_avg, gdp_outlier),
    aes(label = country_name),
    size = 3.2, fontface = "bold", color = "black",
    box.padding = 0.4, point.padding = 0.3, max.overlaps = Inf
  ) +
  scale_fill_manual(values = c("Africa" = "#D55E00", "Asia" = "#0072B2")) +
  scale_y_continuous(labels = comma) +
  labs(x = NULL, y = "GDP per capita (constant 2015 US$)") +
  theme_minimal(base_size = 12) +
  theme(legend.position = "none", panel.grid.minor = element_blank())

fig3b <- ggplot(country_avg, aes(x = continent_2d, y = ef_avg, fill = continent_2d)) +
  geom_boxplot(outlier.shape = NA, alpha = 0.5, width = 0.5) +
  geom_jitter(width = 0.08, size = 1.5, alpha = 0.5, color = "grey30") +
  geom_text_repel(
    data = filter(country_avg, ef_outlier),
    aes(label = country_name),
    size = 3.2, fontface = "bold", color = "black",
    box.padding = 0.4, point.padding = 0.3, max.overlaps = Inf
  ) +
  scale_fill_manual(values = c("Africa" = "#D55E00", "Asia" = "#0072B2")) +
  labs(x = NULL, y = "Ecological Footprint per capita (global hectares)") +
  theme_minimal(base_size = 12) +
  theme(legend.position = "none", panel.grid.minor = element_blank())

fig3 <- fig3a + fig3b +
  plot_annotation(caption = "Points: country averages over 2000–2023. Labels: three highest country averages per region.")  # [R2-16]

fig3
ggsave("figure3_boxplot_outliers.png", fig3, width = 11, height = 5.5, dpi = 300)

# ------------------------------------------------------------
# [R2-16] Figure notes for the manuscript:
#   Figures 1-2: "Lines show the cross-country mean in each region and year; shaded bands
#   show the range (minimum to maximum) across countries. Sample: 43 countries, 2000–2023."
#   Figure 3: "Boxes summarise country averages over 2000–2023; labelled points are the three
#   countries with the highest averages in each region."
# ------------------------------------------------------------
