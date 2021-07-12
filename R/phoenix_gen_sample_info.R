library(tidyverse)

# First sample prop is 1 because that is considered the gold-label
sample_prop <- c(
	1,
	rep(
		each = 200, 
		c(
			0.01, 0.05, 0.1, 0.2, 0.3,0.4, 0.5, 0.65, 0.75,0.875, 1, 1.5, 2, 5, 10, 20
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
