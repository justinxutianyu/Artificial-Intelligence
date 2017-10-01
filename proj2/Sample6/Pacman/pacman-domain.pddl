(define (domain pacman)
  (:requirements :typing)
  (:types pos)
  ;; Define the problem facts
  ;; "?" denotes a variable\, "-" denotes a type
  (:predicates  (At ?p - pos)
                (FoodAt ?p - pos)
                (CapsuleAt ?p - pos)
                (GhostAt ?p - pos)
                (Adjacent ?pos1 ?pos2 - pos)
                (Powered)
  )
  ;; Define the actions
  (:action move
        :parameters (?posCurr ?posNext - pos)
        :precondition (and (At ?posCurr)
                           (Adjacent ?posCurr ?posNext)
                       )
        :effect   (and (At ?posNext)
                       (not  (At ?posCurr) )
                       (not  (FoodAt ?posNext) )
                       (not  (CapsuleAt ?posNext) )
                       (when (Powered) (not (GhostAt ?posNext)))
                   )
   )
)