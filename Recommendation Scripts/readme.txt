#Key notes on the Reko Engine:

The engine has 4 individual algorithms to perform recommendations.
Each algorithm produces 10 recommended titles by applying different scoring rubrics.
Time complexity of the algorithms are O(n*k) where n is the number of user and k is the number of titles.


To perform a recommendation the following flags are set when calling the RekoAPI.py file through the command line:-

cf1 - triggers a weighted content filtering scoring rubric
cf2 - triggers an un-weighted content filtering scoring rubric
cf3 - triggers a summation scoring rubric via collaborative filtering
mf1 - triggers a matrix factorization
add - updates a user's scoring metadata

python rekoAPI.py -crds <database user>, <database password> -reko <reko method>, <user id>, <movie id>, <rating>

*Note: The recommended results are written to the database, the information returned via command line is for error handling.
**Note: The Matrix factorization implemented is flawed, but can be corrected.
**Note: The weighted content filtering implementation has a calculation error but results are still useful.


To add metadata to demo users:-

python populateDB.py -lim <number of movies> -usrs <number of users> -tf filtered(<target file>).txt -yrs <min year>, <max year?
