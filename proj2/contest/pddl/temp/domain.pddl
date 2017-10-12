;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;; Blocks World
;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (domain blocksworld)
  (:requirements :strips)
  (:predicates (on ?x ?y)
               (clear ?x)
               (ontable ?x)
               (holding ?x)
               (handempty)
               )
    
  (:action unstack
             :parameters (?x ?y)
             :precondition (and (handempty) (clear ?x))
             :effect 
             (and (holding ?x) 
                  (not (handempty)) 
                  (clear ?y)))

  (:action stack
             :parameters (?x ?y)
             :precondition 
             (and (holding ?x) 
                  (clear ?y) 
                  (not(handempty)))
             :effect 
             (and (handempty) 
                  (on ?x ?y)))

  (:action pickupfromtable
             :parameters (?x)
             :precondition (and (clear ?x) (handempty))
             :effect 
             (and (not (handempty)) 
                  (holding ?x) 
                  (not(ontable ?x))))

  (:action dropontable
             :parameters (?x)
             :precondition (and (holding ?x))
             :effect (and (handempty) (ontable ?x)))
)

