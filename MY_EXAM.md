## EXERCISE_2
    - My code already does this feature, no new commit needed

## EXERCISE_3
    - Already implemented, using a margin of 75
    - It has a steering value or somewhat when passing though the wall_margin slowing it down the returning it in the opposite direction with the same velocity

## EXERCISE_4
    - Added a collision check and a collision movement functions
    - It multiplies movement vect by -1 

## EXERCISE_5
    - Scraping my collision movement to make space for eating feature and prevent possible bug
    - had to create a clamp size function cause my squares grew too large leading to an eventual bug
    - used the union inbuilt function in pygame, could do without it though

## EXERCISE_6
    - I used 100% proportion and I solved this in the previous exercise

## EXERCISE_7
    - due to time I have currently paused this implementation, but I thing I know what my main issue is, after some thinking I will return to this question.
    - My plan is to update the lines my taking the movement vector into consideration or a directional vector(norm of movement vector) in other to know which direction the line should be drawn in.

## EXERCISE_8
    - I believe that the test should be checked by an assertation check, I have just forgotten how to write assert equal or in range functions, or which module to import. but overrall, we check if the square speed is withing our clamped square speed.