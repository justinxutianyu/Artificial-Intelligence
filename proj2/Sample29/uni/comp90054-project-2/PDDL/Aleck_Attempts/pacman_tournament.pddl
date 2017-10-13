(define (domain pacman)
	(:requirements :action-costs)
	(:functions
		(total-cost)
	)
	(:predicates
		(isLeftSide)
		(curLoc ?x ?y)
		(locA ?x ?y)
		(left ?x1 ?y1 ?x2 ?y2)
		(right ?x1 ?y1 ?x2 ?y2)
		(down ?x1 ?y1 ?x2 ?y2)
		(up ?x1 ?y1 ?x2 ?y2)
		(leftSideSquare ?x ?y)
		(locEnemy ?x ?y)
		(locPEnemy ?x ?y)
		(locP ?x ?y)
		(locF ?x ?y)
		(ppA)
		(isGhost)
	)
	(:action moveUp
		:parameters ?x1 ?y1 ?x2 ?y2
		:precondition
			(and
				(up x1 y1 x2 y2)
				(curloc x1 y1)
				(not (locA x2 y2))
				(or
					(not (locEnemy x2 y2))
					(ppA)
					(and
						(isGhost)
						(not (locPEnemy x2 y2))
					)
				)
			)
		:effect
			(and
				(loc a x2 y2)
				(not (locA x1 y1))
				(not (locF x2 y2))
				(increase total-cost 1)
			)
	)
	(:action moveDown
		:parameters ?x1 ?y1 ?x2 ?y2
		:precondition
			(and
				(down x1 y1 x2 y2)
				(curloc x1 y1)
				(not (locA x2 y2))
				(or
					(not (locEnemy x2 y2))
					(ppA)
					(and
						(isGhost)
						(not (locPEnemy x2 y2))
					)
				)
			)
		:effect
			(and
				(loc a x2 y2)
				(not (locA x1 y1))
				(not (locF x2 y2))
				(increase total-cost 1)
			)
	)
	(:action moveRight
		:parameters ?x1 ?y1 ?x2 ?y2
		:precondition
			(and
				(right x1 y1 x2 y2)
				(curloc x1 y1)
				(not (locA x2 y2))
				(or
					(not (locEnemy x2 y2))
					(ppA)
					(and
						(isGhost)
						(not (locPEnemy x2 y2))
					)
				)
			)
		:effect
			(and
				(loc a x2 y2)
				(not (locA x1 y1))
				(not (locF x2 y2))
				(increase total-cost 1)
			)
	)
	(:action moveLeft
		:parameters ?x1 ?y1 ?x2 ?y2
		:precondition
			(and
				(left x1 y1 x2 y2)
				(curloc x1 y1)
				(not (locA x2 y2))
				(or
					(not (locEnemy x2 y2))
					(ppA)
					(and
						(isGhost)
						(not (locPEnemy x2 y2))
					)
				)
			)
		:effect
			(and
				(loc a x2 y2)
				(not (locA x1 y1))
				(not (locF x2 y2))
				(increase total-cost 1)
			)
	)
	(:action becomeGhost
		:parameters ?x ?y
		:preconditions
			(and
				(curLoc x y)
				(or
					(and (leftSideSquare x y) (not isLeftSide))
					(and (not (leftSideSquare x y)) (isLeftSide))
				)
			)
		:effect
		 	(isGhost)
	)
	(:action becomeAgent
		:parameters ?x ?y
		:preconditions
			(and
				(curLoc x y)
				(or
					(and (leftSideSquare x y) (isLeftSide))
					(and (not (leftSideSquare x y)) (not (isLeftSide)))
				)
			)
		:effect
		 	(not (isGhost))
	)
	(:action pickUpPP
		:parameters ?x ?y
		:preconditions
			(and
				(curLoc x y)
				(locP x y)
			)
		:effects
			(and
				(not (locP x y))
			 	(ppA)
			)
	)
	(:eatEnemy
		:parameters ?x ?y
		:preconditions
			(and
				(curLoc x y)
				(or
					(isGhost)
					(ppA)
				)
			)
		:effect
			(locEnemy x y)
	)
)
