(define (problem pacman-01)
   (:domain pacman)
   (:objects l00 l01 l02 l03 l04 l10 l11 l12 l13 l14 l20 l21 l22 l23 l24
             l30 l31 l32 l33 l34 l40 l41 l42 l43 l44 - location)
   ;; define the initial situation
   ;; connected define the grid
   ;; foodAt define the food location
   ;; ghostAt define the ghosts
   ;; pacmanAt define the intial location of the pacman and 
   ;; this location will be the home
   (:init (connected l00 l01)
          (connected l02 l03)
          (connected l03 l04)
          (connected l10 l11)
          (connected l11 l12)
          (connected l12 l13)
          (connected l21 l22)
          (connected l22 l23)
          (connected l23 l24)
          (connected l31 l32)
          (connected l30 l31)
          (connected l33 l34)
          (connected l40 l41)
          (connected l41 l42)
          (connected l42 l43)
          (connected l43 l44)
          (connected l01 l00)
          (connected l03 l02)
          (connected l04 l03)
          (connected l11 l10)
          (connected l12 l11)
          (connected l13 l12)
          (connected l22 l21)
          (connected l23 l22)
          (connected l24 l23)
          (connected l32 l31)
          (connected l31 l30)
          (connected l34 l33)
          (connected l41 l40)
          (connected l42 l41)
          (connected l43 l42)
          (connected l44 l43)
          (connected l00 l10)
          (connected l10 l20)
          (connected l20 l30)
          (connected l01 l11)
          (connected l21 l31)
          (connected l31 l41)
          (connected l02 l12)
          (connected l12 l22)
          (connected l22 l32)
          (connected l32 l42)
          (connected l03 l13)
          (connected l13 l23)
          (connected l33 l43)
          (connected l04 l14)
          (connected l14 l24)
          (connected l34 l44)
          (connected l10 l00)
          (connected l20 l10)
          (connected l30 l20)
          (connected l11 l01)
          (connected l31 l21)
          (connected l41 l31)
          (connected l12 l02)
          (connected l22 l12)
          (connected l32 l22)
          (connected l42 l32)
          (connected l13 l03)
          (connected l23 l13)
          (connected l43 l33)
          (connected l14 l04)
          (connected l24 l14)
          (connected l44 l34)
          (pacmanAt l00)
          (foodAt l30)
          (foodAt l22)
          (foodAt l04)
          (foodAt l34)
          (ghostAt l20)
          (ghostAt l14)
          (capsuleAt l10)
   )
   (:goal (and (not (foodAt l30))
               (not (foodAt l22))
               (not (foodAt l04))
               (not (foodAt l34))
               (pacmanAt l00)
   ))
)