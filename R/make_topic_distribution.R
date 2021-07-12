library(tidytext)
p_td_d_path <- "data/Samples/p_td_d1_0.csv"
words_all_path <- "data/Samples/words_all_0.csv"
docs_all_path <- "data/Samples/docs_all_0.csv"
p_tw_td_path <- "data/Samples/p_tw_td1_0.csv"
p_w_tw_path <- "data/Samples/p_w_tw1_0.csv"

read_csv("../Phoenix-Sampling/data/clean_posts.csv") %>% 
	unnest_tokens(word, Content) %>% 
	group_by(Post_ID) %>% 
	summarise(count = n()) %>% 
	summarise(mean_count = mean(count))

words_all <- tibble(words_all_path = words_all_path) %>% 
	mutate(
		words = map(
			words_all_path,
			~read_csv(.x) %>% 
				mutate(word_ID = X1 + 1, word = `0`) %>% 
				select(word_ID, word)
		)) %>% 
	select(-words_all_path) %>% 
	unnest(words) 

docs_all <- tibble(docs_all_path = docs_all_path) %>% 
	mutate(
		docs = map(
			docs_all_path,
			~read_csv(.x) %>% 
				mutate(doc_ID = X1 + 1, doc = `0`) %>% 
				select(doc_ID, doc)
		)) %>% 
	select(-docs_all_path) %>% 
	unnest(docs) 

doc_topics <- read_csv(p_td_d_path) %>%
	select(doc_topic = X1, everything()) %>%
	mutate(doc_topic = doc_topic + 1) %>% 
	gather("doc_ID", "p", -doc_topic) %>% 
	mutate(doc_ID = as.numeric(doc_ID) + 1) %>% 
	filter(p > 0) %>% 
	group_by(doc_ID) %>% 
	group_by(doc_topic) %>% 
	summarise(count = n()) %>% 
	ungroup() %>% 
	transmute(doc_topic, p = count/sum(count))


	read_csv(p_tw_td_path) %>% 
	select(word_topic = X1, everything()) %>%
	mutate(word_topic = word_topic + 1) %>% 
	gather("doc_topic", "p", -word_topic) %>% 
	mutate(doc_topic = as.numeric(doc_topic) + 1) %>% 
	group_by(doc_topic) %>% 
		summarise(p = sum(p))

		
	