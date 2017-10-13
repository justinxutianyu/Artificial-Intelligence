(define (domain pacman)
	(:requirements :action-costs)
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
		(clearAgent ?x ?y)
		(clearEnemy ?x ?y)
		(clearPenemy ?x ?y)
		(wall ?x ?y)
		(ppA ?a)
		(isPP ?x ?y)
		(isFood ?x ?y)
		(isGhost ?a)
	)
	(:action moveUp
		:parameters ?a ?x1 ?y1 ?x2 ?y2
		:precondition
			(and
				(up x1 y1 x2 y2)
				(loc a x1 y1)
				(not (wall x2 y2))
				(clearAgent x2 y2)
				(or
					(clearEnemy x2 y2)
					(ppA a)
					(and
						(isGhost a)
						(clearPenemy x2 y2)
					)
				)
			)
		:effect
			(and
				(loc a x2 y2)
				(not (loc a x1 y1))
				(not (isFood x2 y2))
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
				(clearAgent x2 y2)
				(or
					(clearEnemy x2 y2)
					(ppA a)
					(and
						(isGhost a)
						(clearPenemy x2 y2)
					)
				)
			)
		:effect
			(and
				(loc a x2 y2)
				(not (loc a x1 y1))
				(not (isFood x2 y2))
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
				(clearAgent x2 y2)
				(or
					(clearEnemy x2 y2)
					(ppA a)
					(and
						(isGhost a)
						(clearPenemy x2 y2)
					)
				)
			)
		:effect
			(and
				(loc a x2 y2)
				(not (loc a x1 y1))
				(not (isFood x2 y2))
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
				(clearAgent x2 y2)
				(or
					(clearEnemy x2 y2)
					(ppA a)
					(and
						(isGhost a)
						(clearPenemy x2 y2)
					)
				)
			)
		:effect
			(and
				(loc a x2 y2)
				(not (loc a x1 y1))
				(not (isFood x2 y2))
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
	(:action pickUpPP
		:parameters ?a ?x ?y
		:preconditions
			(and
				(loc a x y)
				(isPP x y)
			)
		:effects
			(and
				(not (isPP x y))
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
			(and
				(clearEnemy x y)
			)
	)
)
