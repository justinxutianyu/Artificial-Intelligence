(define (domain pacman-strips)
	(:predicates (AGENT_AT ?x) (ENEMY_PHANTOM_AT ?x) (ENEMY_PACMAN_AT ?x) (PHANTOM_AT ?x)
		(PACMAN_AT ?x) (CHEESE_AT ?x) (CHEER_AT ?x) (CAN_GO ?x ?y) (CHEESE_COUNT ?x) (VISITED_AT ?x)
	)
	(:action move :parameters(?x ?y)
		:precondition (and (AGENT_AT ?x) (CAN_GO ?x ?y))
		:effect (and (AGENT_AT ?y) (VISITED_AT ?y) (not (AGENT_AT ?x)))
	)
	(:action eat :parameters(?x ?y)
		:precondition (and (AGENT_AT ?x) (CAN_GO ?x ?y) (PACMAN_AT ?x) (CHEESE_AT ?y))
		:effect (and (AGENT_AT ?y) (PACMAN_AT ?y) (VISITED_AT ?y) (not (AGENT_AT ?x)) (not (PACMAN_AT ?x)) (not (CHEESE_AT ?y)))
	)
	(:action eat-power :parameters(?x ?y)
		:precondition (and (AGENT_AT ?x) (CAN_GO ?x ?y) (PACMAN_AT ?x) (CHEER_AT ?y))
		:effect (and (AGENT_AT ?y) (PACMAN_AT ?y) (VISITED_AT ?y) (not (AGENT_AT ?x)) (not (PACMAN_AT ?x)) (not (CHEER_AT ?y)))
	)
	(:action kill-pacman :parameters(?x ?y)
		:precondition (and (AGENT_AT ?x) (CAN_GO ?x ?y) (PHANTOM_AT ?x) (ENEMY_PACMAN_AT ?y))
		:effect (and (AGENT_AT ?y) (PHANTOM_AT ?y) (VISITED_AT ?y) (not (AGENT_AT ?x)) (not (PHANTOM_AT ?x)) (not (ENEMY_PACMAN_AT ?y)))
	)
)
