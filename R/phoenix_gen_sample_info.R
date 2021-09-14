library(tidyverse)

# First sample prop is 1 because that is considered the gold-label
sample_prop <- c(
	1,
	rep(
		each = 200, 
		2^c(
		1:11	
		)
	)
)

# Testing by only having 2 small samples
#sample_prop <- sample_prop[2:3]

tibble(sample_prop = sample_prop) %>% 
	mutate(sample = (1:n())-1) %>% 
write_csv(path = "data/Samples.info/samples.csv")

paste("n_samp=", length(sample_prop)-1, sep = "") %>% 
	write(file = "n_samp")
