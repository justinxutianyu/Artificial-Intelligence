(define (problem ghost)
    (:domain ghost-pacman-not-moving)
    (:objects A1 A2 A3 A4 B1 B2 B3 C1 C3 C4 D1 D2 D3 D4 - square)
    ;; to represent a wall, we simply blank out the space that contains the wall
    ;; eg: if B4 is a wall, then there is no B4.
    
    ;; there are only two walls in this problem: B4 and C2.
    
    ;;defining the initial situaition:
    (:init  (connected A1 A2)
            (connected A2 A3)
            (connected A3 A4)
            (connected A1 B1)
            (connected A2 B2)
            (connected A3 B3)
            (connected B1 B2)
            (connected B2 B3)
            (connected B1 C1)
            (connected B3 C3)
            (connected C3 C4)
            (connected C1 D1)
            (connected C3 D3)
            (connected C4 D4)
            (connected D1 D2)
            (connected D2 D3)
            (connected D3 D4)
            
            ;; now reverse all these one way connections
            
            (connected A2 A1)
            (connected A3 A2)
            (connected A4 A3)
            (connected B1 A1)
            (connected B2 A2)
            (connected B3 A3)
            (connected B2 B1)
            (connected B3 B2)
            (connected C1 B1)
            (connected C3 B3)
            (connected C4 C3)
            (connected D1 C1)
            (connected D3 C3)
            (connected D4 C4)
            (connected D2 D1)
            (connected D3 D2)
            (connected D4 D3)
            
            ;;initialise placement of pacman, food items and ghost.
            
            ;;assumption: only one pacman and one ghost in this problem.
            ;;assumption: pacman does not move.
            ;;assumption: food is not important for the ghost
            
            ;;(food_at C3)
            ;;(food_at D4)
            (ghost_at D2)
            (pacman_at A1)
    )
            
    
    ;;goal situation: eat the pacman, and make him dissappear. (refer to domain)
    (:goal
        (not (pacman_at A1))
    )
    
)