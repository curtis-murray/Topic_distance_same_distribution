library(tidyverse)

# More samples between a and b than between b and c (we don't care as much for the full data)
a = 0
b = 0.5
c = 1

n1 = 20
n2 = 5

# First sample prop is 1 because that is considered the gold-label
sample_prop <- c(
	1,
	rep(
		each = 10, 
		c(
			seq(a+(b-a)/n1, b, length.out = n1), 
			seq(b+(c-b)/n2, c, length.out = n2)
		)
	),
	rep(
	  each = 100, 
	  c(
	    0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1
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
