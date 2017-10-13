(define (domain ghost-pacman-not-moving)

    (:requirements
        :typing
    )

    (:types square)
    
    ;;assumption: ghost needs not to know where the food is
    (:predicates 
                (ghost_at ?pos -square)
                (connected ?start ?end -square)
                (pacman_at ?pac_pos -square)
               
    )

    (:action moveNormally
        :parameters (?start ?end -square)
        :precondition (and  (connected ?start ?end)
                            (ghost_at ?start)
                            (not (pacman_at ?end))
                        )
        :effect (and (not (ghost_at ?start))
                          (ghost_at ?end)
                )
    )
    
    ;;assumption: pacman just dissappears when ghost eats him. poor pacman ):
    (:action moveToEatPacman
        :parameters (?start ?end -square)
        :precondition (and  (connected ?start ?end)
                            (ghost_at ?start)
                            (pacman_at ?end)
                        )
        :effect (and (not (ghost_at ?start))
                          (ghost_at ?end)
                     (not (pacman_at ?end))
                )
    )
)