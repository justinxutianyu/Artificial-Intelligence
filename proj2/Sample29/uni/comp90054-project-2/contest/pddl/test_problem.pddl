(define (problem test-problem)
	(:domain test-domain)
	(:objects an-object )
	(:init (and (is-a-predicate ?x)))
	(:goal (not (is-a-predicate ?x))))
