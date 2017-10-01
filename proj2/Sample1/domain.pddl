; The University of Melbourne
; COMP90054 Software Agents
; Project 2, 2013

; Team PacMania:
; Aram Kocharyan, aramk, 359867
; Brendan Studds, bpstudds, 269713
; John Fulton, jful, 269328
; Yichang Zhang, yichangz, 542656

; This PDDL formulates the classic version of PacMan, not the tournament version
; in this project. The goal for a PacMan agent is to eat all food (and power
; pellets) while avoiding ghosts. The goal for a Ghost agent is to eat PacMan
; and avoid being eaten via the power pellets. These two perspectives would have
; their own problem files which use this shared domain file.

; We continue to assume a static environment for each execution of the planner.

; PacMan's goal would be to eat all food: all FOOD_AT from the initial state is
; EATEN_FOOD_AT ; in the goal.
; A Ghost's goal would be to have VISITED_AT where PACMAN_AT is in the intial
; state.

(define (domain pacman-strips)
  (:predicates
    (AGENT_AT ?x) ; Position of the current agent - either PacMan or a Ghost.
    (PACMAN_AT ?x) ; Position of PacMan
    (FOOD_AT ?x) ; Position of food (not including power pellets)
    (POWER_AT ?x) ; Position of power pellets

    (CAN_GO ?x ?y) ; Whether we can move from position x to y.
      ; This is determined by the lack of walls, but is clearer than NO_WALL_AT
      ; and allows us to represent more constraints later without the need to
      ; modify existing preconditons. Also note preconditions cannot be
      ; explicitly negated in PDDL.
      
    (SCARY_GHOST_AT ?x) ; Position of a ghost which can eat PacMan.
    (EDIBLE_GHOST_AT ?x) ; Position of a ghost PacMan can eat due to eating
      ; a power pellet. This is considered mutually exclusive to SCARY_GHOST_AT.
    (VISITED_AT ?x) ; Indicates that we have already visited a certain position.

    ; This isn't used in any current actions, but is left here for completeness.
    ; VISITED_AT should be sufficient for specifying travel goals.
    (EATEN_FOOD_AT ?x) ; Position of food that was eaten.
    (EATEN_POWER_AT ?x) ; Position of power pellet that was eaten.
  )

  (:action move-pacman :parameters(?x ?y)
    :precondition (and (AGENT_AT ?x) (PACMAN_AT ?x) (CAN_GO ?x ?y))
    :effect (and (AGENT_AT ?y) (PACMAN_AT ?y) (VISITED_AT ?y)
      (not (AGENT_AT ?x)) (not (PACMAN_AT ?x)))
  )
  (:action move-ghost-scary :parameters(?x ?y)
    :precondition (and (AGENT_AT ?x) (SCARY_GHOST_AT ?x) (CAN_GO ?x ?y))
    :effect (and (AGENT_AT ?y) (SCARY_GHOST_AT ?y) (VISITED_AT ?y)
      (not (AGENT_AT ?x)) (not (SCARY_GHOST_AT ?x)))
  )
  (:action move-ghost-edible :parameters(?x ?y)
    ; CAN_GO is populated with both the wall positions and the PACMAN_AT
    ; positions in the initial problem
    :precondition (and (AGENT_AT ?x) (EDIBLE_GHOST_AT ?x) (CAN_GO ?x ?y))
    :effect (and (AGENT_AT ?y) (EDIBLE_GHOST_AT ?y) (VISITED_AT ?y)
      (not (AGENT_AT ?x)) (not (EDIBLE_GHOST_AT ?x)))
  )
  (:action eat-food :parameters(?x ?y)
    :precondition (and (AGENT_AT ?x) (CAN_GO ?x ?y) (PACMAN_AT ?x) (FOOD_AT ?y))
    :effect (and (AGENT_AT ?y) (PACMAN_AT ?y) (VISITED_AT ?y)
      (not (AGENT_AT ?x)) (not (PACMAN_AT ?x)) (not (FOOD_AT ?y)))
  )
  (:action eat-power :parameters(?x ?y)
    :precondition (and (AGENT_AT ?x) (CAN_GO ?x ?y) (PACMAN_AT ?x)
      (POWER_AT ?y))
    :effect (and (AGENT_AT ?y) (PACMAN_AT ?y) (VISITED_AT ?y)
      (not (AGENT_AT ?x)) (not (PACMAN_AT ?x)) (not (POWER_AT ?y)))
  )
  (:action eat-ghost :parameters(?x ?y)
    :precondition (and (AGENT_AT ?x) (PACMAN_AT ?x) (CAN_GO ?x ?y)
      (EDIBLE_GHOST_AT ?y))
    :effect (and (AGENT_AT ?y) (PACMAN_AT ?y) (VISITED_AT ?y)
      (not (AGENT_AT ?x)) (not (PACMAN_AT ?x)) (not (EDIBLE_GHOST_AT ?y)))
  )
  (:action eat-pacman :parameters(?x ?y)
    :precondition (and (AGENT_AT ?x) (SCARY_GHOST_AT ?x) (CAN_GO ?x ?y)
      (PACMAN_AT ?y))
    :effect (and (AGENT_AT ?y) (SCARY_GHOST_AT ?y) (VISITED_AT ?y)
      (not (AGENT_AT ?x)) (not (SCARY_GHOST_AT ?x)) (not (PACMAN_AT ?y)))
  )

)
