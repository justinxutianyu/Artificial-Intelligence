(define (domain ghost)
    (:requirements :typing)
    (:types location)

    ;; define facts in the problem 
    (:predicates  (pacmanAt ?posPacman - location)
                  (ghostAt ?posGhost - location)
                  (connected ?posFrom ?posTo - location) 
                  (eatCapsule) ;; if the pacman has eaten the capsule
                )
    ;; define the actions 
   (:action move ;; move or eat a pacman
               :parameters (?from ?to - location)
               :precondition (and (ghostAt ?from)
                                   (connected ?from ?to)
                                   (not (pacmanAt ?to))
                              )
               :effect (and (ghostAt ?to) ;; change the position of ghost
                             (not (ghostAt ?from))
                        )
   )
   (:action move_to_eat_pacman
               :parameters (?from ?to - location)
               :precondition (and (ghostAt ?from)
                                   (connected ?from ?to)
                                   (pacmanAt ?to)
                                   (not (eatCapsule))
                              )
               :effect (and (ghostAt ?to) ;; change the position of ghost
                             (not (ghostAt ?from))
                             (not (pacmanAt ?to))
                        )
   )
)
    