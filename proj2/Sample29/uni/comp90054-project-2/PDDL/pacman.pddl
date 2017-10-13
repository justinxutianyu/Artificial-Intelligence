(define (domain pacman)

(:predicates
    (loc(?a ?x ?y))
    (wall(?x ?y))
    (pp-loc(?p ?x ?y))
    (pp-agent(?a))
    (pp-enemy(?e))
    (enemy-loc(?e))
    (food-loc(?f ?x ?y))
    (is-ghost ?a)
    (clear ?x ?y)
    (start-left)
    (half-arena))

(:action move-down
    :parameters(?x ?y)
    :precondition((and (clear ?x ?y)))
    :effect(and (clear ?x ?y) (not (clear ?x ?y - 1)))

(:action move-up
    :parameters(?x ?y)
    :precondition((and (clear ?x ?y)))
    :effect(and (clear ?x ?y) (not (clear ?x ?y + 1)))

(:action move-left
    :parameters(?x ?y)
    :precondition((and (clear ?x ?y)))
    :effect(and (clear ?x ?y) (not (clear ?x - 1 ?y))))

(:action move-right
    :parameters(?x ?y)
    :precondition((and (clear ?x ?y)))
    :effect(and (clear ?x ?y) (not (clear ?x + 1 ?y))))
