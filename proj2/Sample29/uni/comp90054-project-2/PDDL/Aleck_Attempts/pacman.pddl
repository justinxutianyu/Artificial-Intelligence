(define (domain pacman)
	(:requirements :action-costs :adl)
	(:functions
		(total-cost)
	)
	(:predicates
		(areRed)
		(loc ?a ?x ?y)
		(left ?x1 ?y1 ?x2 ?y2)
		(right ?x1 ?y1 ?x2 ?y2)
		(down ?x1 ?y1 ?x2 ?y2)
		(up ?x1 ?y1 ?x2 ?y2)
		(isRedSide ?x ?y)
		(locEnemy ?e ?x ?y)
		(locP ?x ?y)
		(locF ?x ?y)
		(wall ?x ?y)
		(ppA ?a)
		(ppE ?e)
		(isGhost ?a)
	)
	(:action moveUp
		:parameters ?a ?x1 ?y1 ?x2 ?y2
		:precondition
			(and
				(up x1 y1 x2 y2)
				(loc a x1 y1)
				(not (wall x2 y2))
				(forall (?A) (not (loc A x2 y2)))
				(or
					(forall (?E) (not (locEnemy E x2 y2)))
					(ppA a)
					(and
						(isGhost a)
						(forall (?PE)
							(not
								(and
									(ppE PE)
									(locEnemy PE x2 y2)
								)
							)
						)
					)
				)
			)
		:effect
			(and
				(loc a x2 y2)
				(not (loc a x1 y1))
				(not (locF x2 y2))
				(increase total-cost 1)
			)
	)
	(:action moveDown
		:parameters ?a ?x1 ?y1 ?x2 ?y2
		:precondition
			(and
				(down x1 y1 x2 y2)
				(loc a x1 y1)
				(not (wall x2 y2))
				(forall (?A) (not (loc A x2 y2)))
				(or
					(forall (?E) (not (locEnemy E x2 y2)))
					(ppA a)
					(and
						(isGhost a)
						(forall (?PE)
							(not
								(and
									(ppE PE)
									(locEnemy PE x2 y2)
								)
							)
						)
					)
				)
			)
		:effect
			(and
				(loc a x2 y2)
				(not (loc a x1 y1))
				(not (locF F x2 y2))
				(increase total-cost 1)
			)
	)
  	(:action moveRight
		:parameters ?a ?x1 ?y1 ?x2 ?y2
		:precondition
			(and
				(right x1 y1 x2 y2)
				(loc a x1 y1)
				(not (wall x2 y2))
				(forall (?A) (not (loc A x2 y2)))
				(or
					(forall (?E) (not (locEnemy E x2 y2)))
					(ppA a)
					(and
						(isGhost a)
						(forall (?PE)
							(not
								(and
									(ppE PE)
									(locEnemy PE x2 y2)
								)
							)
						)
					)
				)
			)
		:effect
			(and
				(loc a x2 y2)
				(not (loc a x1 y1))
				(not (locF F x2 y2))
				(increase total-cost 1)
			)
	)
  	(:action moveLeft
		:parameters ?a ?x1 ?y1 ?x2 ?y2
		:precondition
			(and
				(left x1 y1 x2 y2)
				(loc a x1 y1)
				(not (wall x2 y2))
				(forall (?A) (not (loc A x2 y2)))
				(or
					(forall (?E) (not (locEnemy E x2 y2)))
					(ppA a)
					(and
						(isGhost a)
						(forall (?PE)
							(not
								(and
									(ppE PE)
									(locEnemy PE x2 y2)
								)
							)
						)
					)
				)
			)
		:effect
			(and
				(loc a x2 y2)
				(not (loc a x1 y1))
				(not (locF F x2 y2))
				(increase total-cost 1)
			)
	)
	(:action becomeGhost
		:parameters ?a ?x ?y
		:preconditions
			(and
				(loc a x y)
				(or
					(and (isRedSide x y) (not areRed))
					(and (not (isRedSide x y)) (areRed))
				)
			)
		:effect
		 	(isGhost a)
	)
	(:action becomeAgent
		:parameters ?a ?x ?y
		:preconditions
			(and
				(loc a x y)
				(or
					(and (isRedSide x y) (areRed))
					(and (not (isRedSide x y)) (not (areRed)))
				)
			)
		:effect
		 	(not (isGhost a))
	)
	(:action pickUpPP
		:parameters ?a ?x ?y
		:preconditions
			(and
				(loc a x y)
				(locP x y)
			)
		:effects
			(and
				(not (locP x y))
			 	(ppA a)
			)
	)
	(:eatEnemy
		:parameters ?a ?x ?y
		:preconditions
			(and
				(loc a x y)
				(or
					(isGhost a)
					(ppA a)
				)
			)
		:effect
			(forall (?E) (locEnemy E x y))
	)
)
