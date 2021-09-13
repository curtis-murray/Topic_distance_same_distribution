library(tidyverse)

read_csv("data/all_docs.csv") %>% 
	transmute(title, Content = content, type, Post_ID = 1:n()) %>% 
	write_csv("data/clean_posts.csv")
