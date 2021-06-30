library(tidyverse)
library(Matrix)
library(matrixStats)
library(stringr)
library(tidytext)
library(dtplyr)
library(data.table)
library(tidyfast)
# ----------------------------------------------------------------
# Loading Data
# <- read_csv("data/Cities/Topic_Model/Samples/Network/adj.csv")

# ----------------------------------------------------------------
# Functions

# ----------------------------------------------------------------

# Get the full (relative to Phoenix folder) paths of the p_w_tw (prob(word|topic))
p_w_tw_all_path <- list.files(path = "data/Samples/", pattern="p_w_tw*")
p_w_tw_all_path <- paste("data/Samples/", p_w_tw_all_path, sep = "")

words_all_all_path <- list.files(path = "data/Samples/", pattern = "words_all*")
words_all_all_path <-paste("data/Samples/", words_all_all_path, sep = "")

# Get the full vocab
# Vocab <- read_csv(words_all_all_path[str_detect(words_all_all_path, "Full")]) %>% 
# 	select(word = `0`)

Vocab <- read_csv("data/clean_posts.csv") %>% 
  unnest_tokens(word, Content) %>% 
  group_by(word) %>%
  summarise(count = n()) %>% 
  mutate(freq = count/sum(count)) %>% 
  arrange(word) %>% 
  mutate(word_ID_full = 1:n())

write_csv(Vocab, "data/Vocab/Vocab.csv")

# Samples info
tibble(p_w_tw_all_path = p_w_tw_all_path) %>% 
  mutate(Sample_prop = str_extract(p_w_tw_all_path, "(?<=_)\\d(.\\d{1,})*(?=_)"),
         Sample = str_extract(p_w_tw_all_path, "(?<=_)\\d{1,}(?=.csv)"),
         Level = str_extract(p_w_tw_all_path, "(?<=p_w_tw)\\d{1,}"),
  ) %>% 
  map_at(c("Sample_prop", "Sample"), as.double) %>% 
  as_tibble() %>% 
  group_by(Sample, Sample_prop) %>% 
  summarise() %>% 
  mutate(Sample_prop = round(Sample_prop, 5)) %>%
  write_csv("data/Samples.info/samples_info.csv")
# Read all p_w_tw files and get adjacency word-topic matrix, join words, construct full word-topic matrix

samples <-  words_all_all_path %>% 
  str_extract("(?<=_)\\d{1,}(?=.csv)")

for(sample in samples){
  probs <- tibble(p_w_tw_all_path = p_w_tw_all_path) %>% 
    mutate(Sample_prop = str_extract(p_w_tw_all_path, "(?<=_)\\d(.\\d{1,})*(?=_)"),
           Sample = str_extract(p_w_tw_all_path, "(?<=_)\\d{1,}(?=.csv)"),
           Level = str_extract(p_w_tw_all_path, "(?<=p_w_tw)\\d{1,}"),
    ) %>% 
    filter(Sample == sample) %>%  # TODO Make this a variable
    map_at(c("Sample_prop", "Sample","Level"), as.double) %>% 
    as_tibble() %>% 
    arrange(-Sample) %>% 
    mutate(
      mat = map(
        p_w_tw_all_path, 
        ~read_csv(.x) %>%
          select(word_ID = X1, everything()) %>%
          mutate(word_ID = word_ID + 1) %>% 
          gather("topic", "p", -word_ID) %>% 
          mutate(topic = as.numeric(topic) + 1) %>% 
          filter(p > 0)
      )) %>% 
    ungroup() %>% 
    arrange(Sample, Sample_prop, Level) %>% 
    mutate(Full = ifelse(Sample_prop == 1,1,0)) %>% 
    group_by(Sample,Full) %>% 
    nest() %>% 
    group_by(Full) %>% 
    mutate(tmp = 1:n()) %>% 
    ungroup() %>% 
    mutate(Full = ifelse((Full) & (tmp == 1),1,0)) %>% 
    mutate(Sample = ifelse(Full, 0, Sample)) %>% 
    unnest() %>% 
    select(Sample,Sample_prop, Level, mat) %>% 
    arrange(Sample, Level)
  
  
  # probs %>% 
  #   select(Sample, Sample_prop) %>% 
  #   group_by(Sample, Sample_prop) %>% 
  #   summarise() %>% 
  #   write_csv("data/Samples.info/samples_info.csv")
  
  words_all <- tibble(words_all_all_path = words_all_all_path) %>% 
    mutate(Sample_prop = str_extract(words_all_all_path, "(?<=_)\\d(.\\d{1,})*(?=_)"),
           Sample = str_extract(words_all_all_path, "(?<=_)\\d{1,}(?=.csv)")) %>% 
    filter(Sample == sample) %>% 
    map_at(c("Sample_prop", "Sample"), as.double) %>% 
    as_tibble() %>% 
    mutate(
      words = map(
        words_all_all_path,
        ~read_csv(.x) %>% 
          mutate(word_ID = X1 + 1, word = `0`) %>% 
          select(word_ID, word)
      )) %>% 
    group_by(Sample) %>% 
    select(-words_all_all_path) %>% 
    ungroup() %>% 
    arrange(Sample, Sample_prop) %>% 
    mutate(Full = ifelse(Sample_prop == 1,1,0)) %>% 
    group_by(Full) %>% 
    mutate(tmp = 1:n()) %>% 
    ungroup() %>% 
    mutate(Full = ifelse((Full) & (tmp == 1),1,0)) %>% 
    mutate(Sample = ifelse(Full, 0, Sample)) %>% 
    select(Sample,Sample_prop, words) %>% 
    arrange(Sample)
  
  # Do we want ALL the vocab in the sampled topic structures? 
  # Penalty could be added after easily. Lets try that.
  
  tidy_topics_full <- probs %>% 
    left_join(words_all, by = c("Sample", "Sample_prop")) %>% 	
    dplyr::mutate(tidy_topics = 
                    map2(mat, words, ~.x %>%
                           full_join(.y, by = "word_ID") %>%
                           left_join(Vocab, by = "word")     # TODO: change to full if necessary
                    )
    ) %>% 
    select(Sample, Sample_prop, Level, tidy_topics) %>% 
    group_by(Sample, Sample_prop) %>% 
    ungroup()
  
  tidy_topics_full %>% 
    unnest(tidy_topics) %>% 
    group_by(Sample, word_ID_full) %>% 
    arrange(Level) %>% 
    summarise(topic = paste(topic, collapse = "-")) %>% 
    write_csv(paste("data/Tidy_Topics/sample_",sample,".csv",sep = ""))
  
  tidy_topics_full %>% 
    filter(Level == max(Level)) %>% 
    unnest(tidy_topics) %>% 
    select(word_ID_full, freq = p) %>% 
    arrange(word_ID_full) %>% 
    write_csv(paste("data/Vocab/sample_",sample,".csv",sep = ""))
}

#n_samp <- tidy_topics_full %>% pull(Sample) %>% max()

#paste("n_samp=",n_samp, sep = "") %>% 
#	write(file = "Scripts/n_samp")