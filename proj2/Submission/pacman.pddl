(define (domain pacman)
    (:requirements :typing)
    (:types location)

    ;; define facts in the problem 
    (:predicates  (pacmanAt ?posPacman - location)
                  (ghostAt ?posGhost - location)
                  (connected ?posFrom ?posTo - location) 
                  (eatCapsule) ;; if the pacman has eaten the capsule
                  (foodAt ?posFood - location)
                  (capsuleAt ?posCapsule - location)
                )
    ;; define the actions

    (:action move_noCapsule ;; pacman normally move with not eaten capsule
               :parameters (?from ?to - location)
               :precondition (and (pacmanAt ?from)
                                   (connected ?from ?to)
                                   (not (ghostAt ?to))
                                   (not (foodAt ?to))
                              )
               :effect (and (pacmanAt ?to) ;; change the position of pacman
                             (not (pacmanAt ?from))
                         )
    )
    (:action move_to_eat_food ;; pacman move to eat food
               :parameters (?from ?to - location)
               :precondition (and (pacmanAt ?from)
                                   (connected ?from ?to)
                                   (not (ghostAt ?to))
                                   (foodAt ?to)
                              )
               :effect (and (pacmanAt ?to)
                             (not (pacmanAt ?from))
                             (not (foodAt ?to)) ;;eaten the food
                        )
    )
    (:action move_to_eat_capsule ;; pacman move to eat capsule
               :parameters (?from ?to - location)
               :precondition (and (pacmanAt ?from)
                                   (connected ?from ?to)
                                   (not (ghostAt ?to))
                                   (capsuleAt ?to)
                               )
               :effect (and (pacmanAt ?to)
                             (not (pacmanAt ?from))
                             (not (capsuleAt ?to)) ;;eaten the capsuletAt
                             (eatCapsule)
                        )            
    )
    (:action move_to_eat_ghost ;;when eaten capsule can eat ghost
               :parameters (?from ?to - location)
               :precondition (and (pacmanAt ?from)
                                   (connected ?from ?to)
                                   (eatCapsule)
                                   (ghostAt ?to)
                               )
               :effect (and (pacmanAt ?to)
                             (not (pacmanAt ?from))
                             (not (ghostAt ?to)) ;;eaten the ghost
                        )  

    )
    
)

    





