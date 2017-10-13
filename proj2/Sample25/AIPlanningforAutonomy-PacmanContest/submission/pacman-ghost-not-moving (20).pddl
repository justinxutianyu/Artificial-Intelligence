(define (domain pacman-ghost-not-moving)

    (:requirements
        :typing
    )

    (:types square)

    (:predicates 
                (pacman_at ?pos -square)
                (connected ?start ?end -square)
                (food_at ?foodSquare -square)
                (ghost_at ?ghostSquare -square)
    )

    (:action moveNormally
        :parameters (?start ?end -square)
        :precondition (and  (connected ?start ?end)
                            (pacman_at ?start)
                            (not (ghost_at ?end))
                            (not (food_at ?end))
                        )
        :effect (and (not (pacman_at ?start))
                          (pacman_at ?end)
                )
    )
    
    (:action moveToEatFood
        :parameters (?start ?end -square)
        :precondition (and  (connected ?start ?end)
                            (pacman_at ?start)
                            (not (ghost_at ?end))
                            (food_at ?end)
                        )
        :effect (and (not (pacman_at ?start))
                          (pacman_at ?end)
                     (not (food_at ?end))
                )
    )
)