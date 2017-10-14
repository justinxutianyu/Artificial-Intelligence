(define (domain ghost)
    (:requirements :typing)
    (:types location)

    ;; define facts in the problem 
    (:predicates  (pacmanAt ?locPacman - location)
                  (ghostAt ?locGhost - location)
                  (connected ?locFrom ?posTo - location) 
                  (super) ;; if the pacman has eaten the capsule
                  (home ?locHome - location)
                )
    ;; define the actions 
   (:action move ;; move 
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
                                   (not (super))
                              )
               :effect (and (ghostAt ?to) ;; change the position of ghost
                             (not (ghostAt ?from))
                             (not (pacmanAt ?to))
                        )
   )
   (:action move_to_eat_superpacman
               :parameters (?from ?to ?home - location)
               :precondition (and (ghostAt ?from)
                                   (connected ?from ?to)
                                   (pacmanAt ?to)
                                   (super)
                                   (home ?home)
                              )
               :effect (and (ghostAt ?home) ;; change the position of ghost
                             (not (ghostAt ?from))
                             (not (super))
                        )

   )
)
    