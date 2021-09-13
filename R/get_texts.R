library(tidyverse)
library(tidytext)

austen_docs <- janeaustenr::austen_books() %>% 
	mutate(text = str_to_lower(text)) %>% 
	group_by(book) %>%
	mutate(new_chapter = str_detect(text,"chapter (\\d{1,}|([mdclxvi]+$))")) %>% 
	group_by(book) %>% 
	mutate(chapter_count = cumsum(new_chapter)) %>% 
	group_by(book) %>% 
	mutate(chapter = ifelse(chapter_count == 0,1,chapter_count)) %>% 
	group_by(book,chapter) %>% 
	unnest_tokens(word, text) %>% 
	summarise(content = paste(word, collapse = " ")) %>% 
	ungroup() %>% 
	#filter(book == "Pride & Prejudice") %>% 
	mutate(title = paste(book, "Chapter", chapter, "Jane Austen", sep = " ")) %>% 
	select(title, content) %>% 
	mutate(type = "Jane Austen")

write_csv(austen_docs,"data/clean_posts.csv")
