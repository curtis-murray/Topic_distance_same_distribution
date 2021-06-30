library(tidyverse)
library(tidytext)
library(latex2exp)
library(ggthemes)

devtools::source_gist("2a1bb0133ff568cbe28d", 
                      filename = "geom_flat_violin.R")

Vocab <- read_csv("data/clean_posts.csv") %>% 
  unnest_tokens(word, Content) %>% 
  group_by(word) %>%
  summarise() %>% 
  arrange(word) %>% 
  mutate(word_ID_full = 1:n())

weighted_d <- list.files("data/Tree_Distance", full.names = TRUE) %>% 
  as_tibble() %>% 
  select(path = value) %>% 
  mutate(data = map(
    path, ~read_csv(.x, col_names = c("Sample",
                                      "distance_unweighted", 
                                      "distance_corpora_weighted", 
                                      "distance_both_ave_weighted",
                                      "distance_full_weighted"))
  )) %>% 
  unnest(data) %>% 
  left_join(read_csv("data/Samples.info/samples_info.csv"), by = "Sample") %>% 
  select(-path) %>% 
  arrange(Sample) 

distances = c(
  "distance_unweighted", 
  "distance_corpora_weighted", 
  "distance_both_ave_weighted",
  "distance_full_weighted"
)

#p <- 
weighted_d %>% 
  pivot_longer(cols = starts_with("distance"),
               names_to = "type",
               values_to = "distance") %>% 
  group_by(Sample_prop) %>% 
  filter(n() > 100) %>% 
  group_by(type) %>% 
  ggplot() + 
  geom_violin(aes(x=Sample_prop, y=distance, group = as.factor(Sample_prop))) + 
  geom_boxplot(aes(x=Sample_prop, y=distance, group = as.factor(Sample_prop))) + 
  theme(legend.position = "bottom") + 
  facet_wrap(~type, scales = "free_y", ncol = 2,labeller = label_parsed) + 
  theme_minimal() + 
  coord_cartesian(ylim = c(0,NA))

for(dist in distances){
  
  summary <- weighted_d %>% pivot_longer(cols = starts_with("distance"),
                                         names_to = "type",
                                         values_to = "distance") %>% 
    filter(type == dist) %>% 
    group_by(Sample_prop) %>% 
    filter(n() > 50) %>% 
    group_by(Sample_prop, type) %>%
    summarise(mean = mean(distance),
              n = n(),
              se = qnorm(0.975)*sd(distance)/sqrt(n),
              lwr = mean-se,
              upr = mean+se,
    ) 
  
  weighted_d %>% 
    pivot_longer(cols = starts_with("distance"),
                 names_to = "type",
                 values_to = "distance") %>% 
    filter(type == dist) %>% 
    group_by(Sample_prop) %>% 
    filter(n() > 50) %>% 
    group_by(type) %>% 
    #mutate(distance = distance/max(distance)) %>% 
    ungroup() %>% 
    left_join(summary) %>% 
    ggplot() 
    
p <- weighted_d %>% 
  pivot_longer(cols = starts_with("distance"),
               names_to = "type",
               values_to = "distance") %>% 
  filter(type == dist) %>% 
  group_by(Sample_prop) %>% 
  filter(n() > 50) %>% 
  group_by(type) %>% 
  #mutate(distance = distance/max(distance)) %>% 
  ungroup() %>% 
  left_join(summary) %>% 
  ggplot(aes(x=Sample_prop, y=distance, group = as.factor(Sample_prop))) +
  #geom_ribbon(aes(x = Sample_prop, ymin = lwr, ymax = upr, group = NA), color = "#E3D8F1", alpha = 0.2, position = "identity")+
  geom_flat_violin(scale = "count",
                   color = "#1B3036",
                   fill = "#336170",
                   width =0.15,
                   #fill = 1,
                   alpha = 0.2,
                   trim = FALSE) + 
  stat_summary(fun.data = mean_sdl,
               color = "#6E5C70",
               #shape = "point",
               size = 0.5,
               fun.args = list(mult = 1),
               geom = "pointrange",
               #geom = "point",
               position = position_nudge(0.01)) +
  # geom_dotplot(binaxis = "y", 
  #              dotsize = 0.1, 
  #              stackdir = "down", 
  #              method = "histodot",
  #              density = 1,
  #              #binwidth = 0.02, 
  #              position = position_nudge(-0.0)) + 
  geom_jitter(aes(x = Sample_prop-0.01, y = distance), alpha = 0.8,width = 0.005, size = 0.4,color = "#548C85")+
  #facet_wrap(~type, scales = "free_y", ncol = 2,labeller = label_parsed) + 
  theme_minimal() + 
  labs(alpha = "test") + 
  coord_cartesian(ylim = c(0,NA), xlim = c(0,1)) + 
  labs(x = "Proportion of documents sampled from corpus",y= "Topic structure distance")

  p %>% ggsave(filename = paste("Figures/distance_violin_",dist,".pdf",sep = ""), 
             device = "pdf",
             height = 6, 
             width=8)

  p %>% ggsave(filename =  paste("../Meeting Reports/Meeting_Book/files/Figures/distance_violin_",dist,".png",sep = ""),
             device = "png", 
             height = 6, 
             width=8)

}

weighted_d %>% pivot_longer(cols = starts_with("distance"),
                            names_to = "type",
                            values_to = "distance") %>% 
  group_by(Sample_prop) %>% 
  filter(n() > 100) %>% 
  group_by(Sample_prop, type) %>%
  summarise(mean = mean(distance),
            n = n(),
            se = qnorm(0.975)*sd(distance)/sqrt(n),
            lwr = mean-se,
            upr = mean+se,
  ) %>% 
  ggplot() + 
  geom_point(aes(x=Sample_prop, y=mean)) +
  geom_line(aes(x=Sample_prop, y=mean)) +
  geom_ribbon(aes(x = Sample_prop, ymin = lwr, ymax = upr), alpha = 0.2) + 
  theme(legend.position = "bottom") + 
  facet_wrap(~type, scales = "free_y", ncol = 2,labeller = label_parsed) + 
  theme_minimal() + 
  labs(alpha = "test") + 
  coord_cartesian(ylim = c(0,NA))

weighted_d %>% pivot_longer(cols = starts_with("distance"),
                            names_to = "type",
                            values_to = "distance") %>% 
  #mutate(distance = distance/max(distance)) %>% 
  ggplot(aes(x = Sample_prop, y = distance,color = type)) + 
  geom_jitter(alpha = 0.1, show.legend = F) + 
  geom_smooth(se = F) + 
  labs(y = "Distance between Topic Structures",
       x = "Sampling Proportion") + 
  theme_minimal() + 
  lims(x = c(0,1)) +
  theme(legend.position = "bottom") + 
  facet_wrap(~type, scales = "free_y", ncol = 2,labeller = label_parsed) + 
  theme(legend.position = "none") + 
  coord_cartesian(ylim = c(0,NA))
p
p %>% ggsave(filename = "Figures/distance.pdf", 
             device = "pdf",
             height = 6, 
             width=8)

p %>% ggsave(filename = "../../Meeting Reports/Meeting_Book/files/Figures/distance.png", 
             device = "png", 
             height = 6, 
             width=8)