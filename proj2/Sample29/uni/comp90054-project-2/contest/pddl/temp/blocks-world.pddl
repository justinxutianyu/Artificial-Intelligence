(define (domain blocks-world)

(:predicates
    (on ?block-a ?block-b)
    (clear ?block)
    (on-table ?block)
    (holding ?block)
    (hand-empty ?hand))

(:action pickup
    :parameters (?block-a, ?block-b, ?hand)
    :precondition (and (hand-empty ?hand) (clear ?block-a))
    :effect (and (holding ?block-a) (clear ?block-b))

(:action dropon
    :parameters (?block-a, ?block-b, ?hand)
    :precondition (and (holding ?block-a) (clear ?block-b) (not(hand-empty ?hand)))
    :effect (and (hand-empty ?hand) (on ?block-a ?block-b)))

(:action pickup-from-table
    :parameters (?block, ?hand)
    :precondition (and (clear ?block) (hand-empty ?hand))
    :effect (and (not(hand-empty ?hand)) (holding ?block) (not(on-table ?block))))

(:action drop-on-table
    :parameters (?block, ?hand)
    :precondition (and (holding ?block))
    :effect (and (hand-empty ?hand) (on-table ?block))))
