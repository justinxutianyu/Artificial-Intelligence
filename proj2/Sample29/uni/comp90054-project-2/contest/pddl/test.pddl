(define (domain test-domain)
	(:requirements :strips)
	(:predicates
		(is-good ?x)
		(is-bad ?x ?y)
	)
	(:action do-this
		:parameters ( ?x ?y)
		:precondition (not (is-bad ?x ?y))
		:effect (and (is-good ?x) (not (is-bad ?x ?y)))))
