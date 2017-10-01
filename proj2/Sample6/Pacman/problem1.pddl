(define (problem pacman-problem)
   (:domain pacman)
   (:objects  p_0_0 p_0_1 p_0_2 p_0_3 p_0_4 p_0_5 p_0_6 p_0_7 p_0_8 p_0_9 p_0_10 p_0_11 p_0_12 p_0_13 p_0_14 p_0_15 p_1_0 p_1_1 p_1_2 p_1_3 p_1_4 p_1_5 p_1_6 p_1_7 p_1_8 p_1_9 p_1_10 p_1_11 p_1_12 p_1_13 p_1_14 p_1_15 p_2_0 p_2_1 p_2_2 p_2_3 p_2_4 p_2_5 p_2_6 p_2_7 p_2_8 p_2_9 p_2_10 p_2_11 p_2_12 p_2_13 p_2_14 p_2_15 p_3_0 p_3_1 p_3_2 p_3_3 p_3_4 p_3_5 p_3_6 p_3_7 p_3_8 p_3_9 p_3_10 p_3_11 p_3_12 p_3_13 p_3_14 p_3_15 p_4_0 p_4_1 p_4_2 p_4_3 p_4_4 p_4_5 p_4_6 p_4_7 p_4_8 p_4_9 p_4_10 p_4_11 p_4_12 p_4_13 p_4_14 p_4_15 p_5_0 p_5_1 p_5_2 p_5_3 p_5_4 p_5_5 p_5_6 p_5_7 p_5_8 p_5_9 p_5_10 p_5_11 p_5_12 p_5_13 p_5_14 p_5_15 p_6_0 p_6_1 p_6_2 p_6_3 p_6_4 p_6_5 p_6_6 p_6_7 p_6_8 p_6_9 p_6_10 p_6_11 p_6_12 p_6_13 p_6_14 p_6_15 p_7_0 p_7_1 p_7_2 p_7_3 p_7_4 p_7_5 p_7_6 p_7_7 p_7_8 p_7_9 p_7_10 p_7_11 p_7_12 p_7_13 p_7_14 p_7_15 p_8_0 p_8_1 p_8_2 p_8_3 p_8_4 p_8_5 p_8_6 p_8_7 p_8_8 p_8_9 p_8_10 p_8_11 p_8_12 p_8_13 p_8_14 p_8_15 p_9_0 p_9_1 p_9_2 p_9_3 p_9_4 p_9_5 p_9_6 p_9_7 p_9_8 p_9_9 p_9_10 p_9_11 p_9_12 p_9_13 p_9_14 p_9_15 p_10_0 p_10_1 p_10_2 p_10_3 p_10_4 p_10_5 p_10_6 p_10_7 p_10_8 p_10_9 p_10_10 p_10_11 p_10_12 p_10_13 p_10_14 p_10_15 p_11_0 p_11_1 p_11_2 p_11_3 p_11_4 p_11_5 p_11_6 p_11_7 p_11_8 p_11_9 p_11_10 p_11_11 p_11_12 p_11_13 p_11_14 p_11_15 p_12_0 p_12_1 p_12_2 p_12_3 p_12_4 p_12_5 p_12_6 p_12_7 p_12_8 p_12_9 p_12_10 p_12_11 p_12_12 p_12_13 p_12_14 p_12_15 p_13_0 p_13_1 p_13_2 p_13_3 p_13_4 p_13_5 p_13_6 p_13_7 p_13_8 p_13_9 p_13_10 p_13_11 p_13_12 p_13_13 p_13_14 p_13_15 p_14_0 p_14_1 p_14_2 p_14_3 p_14_4 p_14_5 p_14_6 p_14_7 p_14_8 p_14_9 p_14_10 p_14_11 p_14_12 p_14_13 p_14_14 p_14_15 p_15_0 p_15_1 p_15_2 p_15_3 p_15_4 p_15_5 p_15_6 p_15_7 p_15_8 p_15_9 p_15_10 p_15_11 p_15_12 p_15_13 p_15_14 p_15_15 p_16_0 p_16_1 p_16_2 p_16_3 p_16_4 p_16_5 p_16_6 p_16_7 p_16_8 p_16_9 p_16_10 p_16_11 p_16_12 p_16_13 p_16_14 p_16_15 p_17_0 p_17_1 p_17_2 p_17_3 p_17_4 p_17_5 p_17_6 p_17_7 p_17_8 p_17_9 p_17_10 p_17_11 p_17_12 p_17_13 p_17_14 p_17_15 p_18_0 p_18_1 p_18_2 p_18_3 p_18_4 p_18_5 p_18_6 p_18_7 p_18_8 p_18_9 p_18_10 p_18_11 p_18_12 p_18_13 p_18_14 p_18_15 p_19_0 p_19_1 p_19_2 p_19_3 p_19_4 p_19_5 p_19_6 p_19_7 p_19_8 p_19_9 p_19_10 p_19_11 p_19_12 p_19_13 p_19_14 p_19_15 p_20_0 p_20_1 p_20_2 p_20_3 p_20_4 p_20_5 p_20_6 p_20_7 p_20_8 p_20_9 p_20_10 p_20_11 p_20_12 p_20_13 p_20_14 p_20_15 p_21_0 p_21_1 p_21_2 p_21_3 p_21_4 p_21_5 p_21_6 p_21_7 p_21_8 p_21_9 p_21_10 p_21_11 p_21_12 p_21_13 p_21_14 p_21_15 p_22_0 p_22_1 p_22_2 p_22_3 p_22_4 p_22_5 p_22_6 p_22_7 p_22_8 p_22_9 p_22_10 p_22_11 p_22_12 p_22_13 p_22_14 p_22_15 p_23_0 p_23_1 p_23_2 p_23_3 p_23_4 p_23_5 p_23_6 p_23_7 p_23_8 p_23_9 p_23_10 p_23_11 p_23_12 p_23_13 p_23_14 p_23_15 p_24_0 p_24_1 p_24_2 p_24_3 p_24_4 p_24_5 p_24_6 p_24_7 p_24_8 p_24_9 p_24_10 p_24_11 p_24_12 p_24_13 p_24_14 p_24_15 p_25_0 p_25_1 p_25_2 p_25_3 p_25_4 p_25_5 p_25_6 p_25_7 p_25_8 p_25_9 p_25_10 p_25_11 p_25_12 p_25_13 p_25_14 p_25_15 p_26_0 p_26_1 p_26_2 p_26_3 p_26_4 p_26_5 p_26_6 p_26_7 p_26_8 p_26_9 p_26_10 p_26_11 p_26_12 p_26_13 p_26_14 p_26_15 p_27_0 p_27_1 p_27_2 p_27_3 p_27_4 p_27_5 p_27_6 p_27_7 p_27_8 p_27_9 p_27_10 p_27_11 p_27_12 p_27_13 p_27_14 p_27_15 p_28_0 p_28_1 p_28_2 p_28_3 p_28_4 p_28_5 p_28_6 p_28_7 p_28_8 p_28_9 p_28_10 p_28_11 p_28_12 p_28_13 p_28_14 p_28_15 p_29_0 p_29_1 p_29_2 p_29_3 p_29_4 p_29_5 p_29_6 p_29_7 p_29_8 p_29_9 p_29_10 p_29_11 p_29_12 p_29_13 p_29_14 p_29_15 p_30_0 p_30_1 p_30_2 p_30_3 p_30_4 p_30_5 p_30_6 p_30_7 p_30_8 p_30_9 p_30_10 p_30_11 p_30_12 p_30_13 p_30_14 p_30_15 p_31_0 p_31_1 p_31_2 p_31_3 p_31_4 p_31_5 p_31_6 p_31_7 p_31_8 p_31_9 p_31_10 p_31_11 p_31_12 p_31_13 p_31_14 p_31_15 - pos)
   (:init 
		(At p_1_2)
		(Adjacent p_1_1 p_1_2)
		(Adjacent p_1_2 p_1_3)
		(Adjacent p_1_2 p_1_1)
		(Adjacent p_1_3 p_1_4)
		(Adjacent p_1_3 p_1_2)
		(Adjacent p_1_4 p_1_5)
		(Adjacent p_1_4 p_1_3)
		(Adjacent p_1_5 p_1_6)
		(Adjacent p_1_5 p_1_4)
		(Adjacent p_1_6 p_1_7)
		(Adjacent p_1_6 p_1_5)
		(Adjacent p_1_7 p_1_8)
		(Adjacent p_1_7 p_1_6)
		(Adjacent p_1_8 p_1_9)
		(Adjacent p_1_8 p_1_7)
		(Adjacent p_1_9 p_1_10)
		(Adjacent p_1_9 p_1_8)
		(Adjacent p_1_10 p_1_11)
		(Adjacent p_1_10 p_1_9)
		(Adjacent p_1_11 p_1_12)
		(Adjacent p_1_11 p_1_10)
		(Adjacent p_1_12 p_1_13)
		(Adjacent p_1_12 p_1_11)
		(Adjacent p_1_13 p_1_14)
		(Adjacent p_1_13 p_1_12)
		(Adjacent p_1_14 p_2_14)
		(Adjacent p_1_14 p_1_13)
		(Adjacent p_2_14 p_1_14)
		(Adjacent p_2_14 p_3_14)
		(Adjacent p_3_1 p_3_2)
		(Adjacent p_3_2 p_3_3)
		(Adjacent p_3_2 p_3_1)
		(Adjacent p_3_3 p_3_4)
		(Adjacent p_3_3 p_3_2)
		(Adjacent p_3_4 p_3_5)
		(Adjacent p_3_4 p_3_3)
		(Adjacent p_3_5 p_3_6)
		(Adjacent p_3_5 p_3_4)
		(Adjacent p_3_6 p_4_6)
		(Adjacent p_3_6 p_3_5)
		(Adjacent p_3_8 p_4_8)
		(Adjacent p_3_10 p_4_10)
		(Adjacent p_3_10 p_3_11)
		(Adjacent p_3_11 p_3_12)
		(Adjacent p_3_11 p_3_10)
		(Adjacent p_3_12 p_3_13)
		(Adjacent p_3_12 p_3_11)
		(Adjacent p_3_13 p_3_14)
		(Adjacent p_3_13 p_3_12)
		(Adjacent p_3_14 p_2_14)
		(Adjacent p_3_14 p_3_13)
		(Adjacent p_4_6 p_3_6)
		(Adjacent p_4_6 p_5_6)
		(Adjacent p_4_6 p_4_7)
		(Adjacent p_4_7 p_5_7)
		(Adjacent p_4_7 p_4_8)
		(Adjacent p_4_7 p_4_6)
		(Adjacent p_4_8 p_3_8)
		(Adjacent p_4_8 p_4_9)
		(Adjacent p_4_8 p_4_7)
		(Adjacent p_4_9 p_4_10)
		(Adjacent p_4_9 p_4_8)
		(Adjacent p_4_10 p_3_10)
		(Adjacent p_4_10 p_5_10)
		(Adjacent p_4_10 p_4_9)
		(Adjacent p_5_1 p_5_2)
		(Adjacent p_5_2 p_6_2)
		(Adjacent p_5_2 p_5_3)
		(Adjacent p_5_2 p_5_1)
		(Adjacent p_5_3 p_5_4)
		(Adjacent p_5_3 p_5_2)
		(Adjacent p_5_4 p_5_5)
		(Adjacent p_5_4 p_5_3)
		(Adjacent p_5_5 p_6_5)
		(Adjacent p_5_5 p_5_6)
		(Adjacent p_5_5 p_5_4)
		(Adjacent p_5_6 p_4_6)
		(Adjacent p_5_6 p_5_7)
		(Adjacent p_5_6 p_5_5)
		(Adjacent p_5_7 p_4_7)
		(Adjacent p_5_7 p_5_6)
		(Adjacent p_5_10 p_4_10)
		(Adjacent p_5_10 p_6_10)
		(Adjacent p_5_12 p_6_12)
		(Adjacent p_5_14 p_6_14)
		(Adjacent p_6_2 p_5_2)
		(Adjacent p_6_2 p_7_2)
		(Adjacent p_6_5 p_5_5)
		(Adjacent p_6_5 p_7_5)
		(Adjacent p_6_9 p_7_9)
		(Adjacent p_6_9 p_6_10)
		(Adjacent p_6_10 p_5_10)
		(Adjacent p_6_10 p_6_11)
		(Adjacent p_6_10 p_6_9)
		(Adjacent p_6_11 p_6_12)
		(Adjacent p_6_11 p_6_10)
		(Adjacent p_6_12 p_5_12)
		(Adjacent p_6_12 p_6_13)
		(Adjacent p_6_12 p_6_11)
		(Adjacent p_6_13 p_7_13)
		(Adjacent p_6_13 p_6_14)
		(Adjacent p_6_13 p_6_12)
		(Adjacent p_6_14 p_5_14)
		(Adjacent p_6_14 p_6_13)
		(Adjacent p_7_1 p_8_1)
		(Adjacent p_7_1 p_7_2)
		(Adjacent p_7_2 p_6_2)
		(Adjacent p_7_2 p_7_3)
		(Adjacent p_7_2 p_7_1)
		(Adjacent p_7_3 p_8_3)
		(Adjacent p_7_3 p_7_2)
		(Adjacent p_7_5 p_6_5)
		(Adjacent p_7_5 p_7_6)
		(Adjacent p_7_6 p_8_6)
		(Adjacent p_7_6 p_7_5)
		(Adjacent p_7_8 p_7_9)
		(Adjacent p_7_9 p_6_9)
		(Adjacent p_7_9 p_8_9)
		(Adjacent p_7_9 p_7_8)
		(Adjacent p_7_13 p_6_13)
		(Adjacent p_7_13 p_8_13)
		(Adjacent p_8_1 p_7_1)
		(Adjacent p_8_1 p_9_1)
		(Adjacent p_8_3 p_7_3)
		(Adjacent p_8_6 p_7_6)
		(Adjacent p_8_6 p_9_6)
		(Adjacent p_8_9 p_7_9)
		(Adjacent p_8_11 p_9_11)
		(Adjacent p_8_11 p_8_12)
		(Adjacent p_8_12 p_8_13)
		(Adjacent p_8_12 p_8_11)
		(Adjacent p_8_13 p_7_13)
		(Adjacent p_8_13 p_9_13)
		(Adjacent p_8_13 p_8_14)
		(Adjacent p_8_13 p_8_12)
		(Adjacent p_8_14 p_8_13)
		(Adjacent p_9_1 p_8_1)
		(Adjacent p_9_1 p_10_1)
		(Adjacent p_9_5 p_9_6)
		(Adjacent p_9_6 p_8_6)
		(Adjacent p_9_6 p_10_6)
		(Adjacent p_9_6 p_9_5)
		(Adjacent p_9_11 p_8_11)
		(Adjacent p_9_11 p_10_11)
		(Adjacent p_9_13 p_8_13)
		(Adjacent p_9_13 p_10_13)
		(Adjacent p_10_1 p_9_1)
		(Adjacent p_10_1 p_11_1)
		(Adjacent p_10_3 p_11_3)
		(Adjacent p_10_6 p_9_6)
		(Adjacent p_10_6 p_11_6)
		(Adjacent p_10_6 p_10_7)
		(Adjacent p_10_7 p_10_6)
		(Adjacent p_10_9 p_11_9)
		(Adjacent p_10_11 p_9_11)
		(Adjacent p_10_13 p_9_13)
		(Adjacent p_10_13 p_11_13)
		(Adjacent p_10_13 p_10_14)
		(Adjacent p_10_14 p_10_13)
		(Adjacent p_11_1 p_10_1)
		(Adjacent p_11_1 p_11_2)
		(Adjacent p_11_2 p_12_2)
		(Adjacent p_11_2 p_11_3)
		(Adjacent p_11_2 p_11_1)
		(Adjacent p_11_3 p_10_3)
		(Adjacent p_11_3 p_11_4)
		(Adjacent p_11_3 p_11_2)
		(Adjacent p_11_4 p_12_4)
		(Adjacent p_11_4 p_11_3)
		(Adjacent p_11_6 p_10_6)
		(Adjacent p_11_6 p_12_6)
		(Adjacent p_11_9 p_10_9)
		(Adjacent p_11_9 p_12_9)
		(Adjacent p_11_13 p_10_13)
		(Adjacent p_11_13 p_12_13)
		(Adjacent p_12_2 p_11_2)
		(Adjacent p_12_2 p_13_2)
		(Adjacent p_12_4 p_11_4)
		(Adjacent p_12_4 p_13_4)
		(Adjacent p_12_6 p_11_6)
		(Adjacent p_12_6 p_13_6)
		(Adjacent p_12_6 p_12_7)
		(Adjacent p_12_7 p_13_7)
		(Adjacent p_12_7 p_12_8)
		(Adjacent p_12_7 p_12_6)
		(Adjacent p_12_8 p_13_8)
		(Adjacent p_12_8 p_12_9)
		(Adjacent p_12_8 p_12_7)
		(Adjacent p_12_9 p_11_9)
		(Adjacent p_12_9 p_12_10)
		(Adjacent p_12_9 p_12_8)
		(Adjacent p_12_10 p_12_11)
		(Adjacent p_12_10 p_12_9)
		(Adjacent p_12_11 p_12_12)
		(Adjacent p_12_11 p_12_10)
		(Adjacent p_12_12 p_13_12)
		(Adjacent p_12_12 p_12_13)
		(Adjacent p_12_12 p_12_11)
		(Adjacent p_12_13 p_11_13)
		(Adjacent p_12_13 p_12_14)
		(Adjacent p_12_13 p_12_12)
		(Adjacent p_12_14 p_13_14)
		(Adjacent p_12_14 p_12_13)
		(Adjacent p_13_1 p_14_1)
		(Adjacent p_13_1 p_13_2)
		(Adjacent p_13_2 p_12_2)
		(Adjacent p_13_2 p_13_1)
		(Adjacent p_13_4 p_12_4)
		(Adjacent p_13_4 p_13_5)
		(Adjacent p_13_5 p_14_5)
		(Adjacent p_13_5 p_13_6)
		(Adjacent p_13_5 p_13_4)
		(Adjacent p_13_6 p_12_6)
		(Adjacent p_13_6 p_13_7)
		(Adjacent p_13_6 p_13_5)
		(Adjacent p_13_7 p_12_7)
		(Adjacent p_13_7 p_14_7)
		(Adjacent p_13_7 p_13_8)
		(Adjacent p_13_7 p_13_6)
		(Adjacent p_13_8 p_12_8)
		(Adjacent p_13_8 p_14_8)
		(Adjacent p_13_8 p_13_7)
		(Adjacent p_13_12 p_12_12)
		(Adjacent p_13_12 p_14_12)
		(Adjacent p_13_14 p_12_14)
		(Adjacent p_13_14 p_14_14)
		(Adjacent p_14_1 p_13_1)
		(Adjacent p_14_1 p_15_1)
		(Adjacent p_14_5 p_13_5)
		(Adjacent p_14_5 p_15_5)
		(Adjacent p_14_7 p_13_7)
		(Adjacent p_14_7 p_15_7)
		(Adjacent p_14_7 p_14_8)
		(Adjacent p_14_8 p_13_8)
		(Adjacent p_14_8 p_15_8)
		(Adjacent p_14_8 p_14_9)
		(Adjacent p_14_8 p_14_7)
		(Adjacent p_14_9 p_14_8)
		(Adjacent p_14_11 p_15_11)
		(Adjacent p_14_11 p_14_12)
		(Adjacent p_14_12 p_13_12)
		(Adjacent p_14_12 p_15_12)
		(Adjacent p_14_12 p_14_11)
		(Adjacent p_14_14 p_13_14)
		(Adjacent p_14_14 p_15_14)
		(Adjacent p_15_1 p_14_1)
		(Adjacent p_15_1 p_16_1)
		(Adjacent p_15_1 p_15_2)
		(Adjacent p_15_2 p_16_2)
		(Adjacent p_15_2 p_15_1)
		(Adjacent p_15_4 p_16_4)
		(Adjacent p_15_4 p_15_5)
		(Adjacent p_15_5 p_14_5)
		(Adjacent p_15_5 p_15_4)
		(Adjacent p_15_7 p_14_7)
		(Adjacent p_15_7 p_16_7)
		(Adjacent p_15_7 p_15_8)
		(Adjacent p_15_8 p_14_8)
		(Adjacent p_15_8 p_16_8)
		(Adjacent p_15_8 p_15_7)
		(Adjacent p_15_11 p_14_11)
		(Adjacent p_15_11 p_16_11)
		(Adjacent p_15_11 p_15_12)
		(Adjacent p_15_12 p_14_12)
		(Adjacent p_15_12 p_15_13)
		(Adjacent p_15_12 p_15_11)
		(Adjacent p_15_13 p_16_13)
		(Adjacent p_15_13 p_15_14)
		(Adjacent p_15_13 p_15_12)
		(Adjacent p_15_14 p_14_14)
		(Adjacent p_15_14 p_16_14)
		(Adjacent p_15_14 p_15_13)
		(Adjacent p_16_1 p_15_1)
		(Adjacent p_16_1 p_17_1)
		(Adjacent p_16_1 p_16_2)
		(Adjacent p_16_2 p_15_2)
		(Adjacent p_16_2 p_16_3)
		(Adjacent p_16_2 p_16_1)
		(Adjacent p_16_3 p_17_3)
		(Adjacent p_16_3 p_16_4)
		(Adjacent p_16_3 p_16_2)
		(Adjacent p_16_4 p_15_4)
		(Adjacent p_16_4 p_17_4)
		(Adjacent p_16_4 p_16_3)
		(Adjacent p_16_7 p_15_7)
		(Adjacent p_16_7 p_17_7)
		(Adjacent p_16_7 p_16_8)
		(Adjacent p_16_8 p_15_8)
		(Adjacent p_16_8 p_17_8)
		(Adjacent p_16_8 p_16_7)
		(Adjacent p_16_10 p_17_10)
		(Adjacent p_16_10 p_16_11)
		(Adjacent p_16_11 p_15_11)
		(Adjacent p_16_11 p_16_10)
		(Adjacent p_16_13 p_15_13)
		(Adjacent p_16_13 p_16_14)
		(Adjacent p_16_14 p_15_14)
		(Adjacent p_16_14 p_17_14)
		(Adjacent p_16_14 p_16_13)
		(Adjacent p_17_1 p_16_1)
		(Adjacent p_17_1 p_18_1)
		(Adjacent p_17_3 p_16_3)
		(Adjacent p_17_3 p_18_3)
		(Adjacent p_17_3 p_17_4)
		(Adjacent p_17_4 p_16_4)
		(Adjacent p_17_4 p_17_3)
		(Adjacent p_17_6 p_17_7)
		(Adjacent p_17_7 p_16_7)
		(Adjacent p_17_7 p_18_7)
		(Adjacent p_17_7 p_17_8)
		(Adjacent p_17_7 p_17_6)
		(Adjacent p_17_8 p_16_8)
		(Adjacent p_17_8 p_18_8)
		(Adjacent p_17_8 p_17_7)
		(Adjacent p_17_10 p_16_10)
		(Adjacent p_17_10 p_18_10)
		(Adjacent p_17_14 p_16_14)
		(Adjacent p_17_14 p_18_14)
		(Adjacent p_18_1 p_17_1)
		(Adjacent p_18_1 p_19_1)
		(Adjacent p_18_3 p_17_3)
		(Adjacent p_18_3 p_19_3)
		(Adjacent p_18_7 p_17_7)
		(Adjacent p_18_7 p_19_7)
		(Adjacent p_18_7 p_18_8)
		(Adjacent p_18_8 p_17_8)
		(Adjacent p_18_8 p_19_8)
		(Adjacent p_18_8 p_18_9)
		(Adjacent p_18_8 p_18_7)
		(Adjacent p_18_9 p_19_9)
		(Adjacent p_18_9 p_18_10)
		(Adjacent p_18_9 p_18_8)
		(Adjacent p_18_10 p_17_10)
		(Adjacent p_18_10 p_18_11)
		(Adjacent p_18_10 p_18_9)
		(Adjacent p_18_11 p_19_11)
		(Adjacent p_18_11 p_18_10)
		(Adjacent p_18_13 p_19_13)
		(Adjacent p_18_13 p_18_14)
		(Adjacent p_18_14 p_17_14)
		(Adjacent p_18_14 p_18_13)
		(Adjacent p_19_1 p_18_1)
		(Adjacent p_19_1 p_19_2)
		(Adjacent p_19_2 p_20_2)
		(Adjacent p_19_2 p_19_3)
		(Adjacent p_19_2 p_19_1)
		(Adjacent p_19_3 p_18_3)
		(Adjacent p_19_3 p_19_4)
		(Adjacent p_19_3 p_19_2)
		(Adjacent p_19_4 p_19_5)
		(Adjacent p_19_4 p_19_3)
		(Adjacent p_19_5 p_19_6)
		(Adjacent p_19_5 p_19_4)
		(Adjacent p_19_6 p_20_6)
		(Adjacent p_19_6 p_19_7)
		(Adjacent p_19_6 p_19_5)
		(Adjacent p_19_7 p_18_7)
		(Adjacent p_19_7 p_19_8)
		(Adjacent p_19_7 p_19_6)
		(Adjacent p_19_8 p_18_8)
		(Adjacent p_19_8 p_19_9)
		(Adjacent p_19_8 p_19_7)
		(Adjacent p_19_9 p_18_9)
		(Adjacent p_19_9 p_20_9)
		(Adjacent p_19_9 p_19_8)
		(Adjacent p_19_11 p_18_11)
		(Adjacent p_19_11 p_20_11)
		(Adjacent p_19_13 p_18_13)
		(Adjacent p_19_13 p_20_13)
		(Adjacent p_20_2 p_19_2)
		(Adjacent p_20_2 p_21_2)
		(Adjacent p_20_6 p_19_6)
		(Adjacent p_20_6 p_21_6)
		(Adjacent p_20_9 p_19_9)
		(Adjacent p_20_9 p_21_9)
		(Adjacent p_20_11 p_19_11)
		(Adjacent p_20_11 p_20_12)
		(Adjacent p_20_12 p_21_12)
		(Adjacent p_20_12 p_20_13)
		(Adjacent p_20_12 p_20_11)
		(Adjacent p_20_13 p_19_13)
		(Adjacent p_20_13 p_20_14)
		(Adjacent p_20_13 p_20_12)
		(Adjacent p_20_14 p_21_14)
		(Adjacent p_20_14 p_20_13)
		(Adjacent p_21_1 p_21_2)
		(Adjacent p_21_2 p_20_2)
		(Adjacent p_21_2 p_22_2)
		(Adjacent p_21_2 p_21_1)
		(Adjacent p_21_4 p_22_4)
		(Adjacent p_21_6 p_20_6)
		(Adjacent p_21_8 p_21_9)
		(Adjacent p_21_9 p_20_9)
		(Adjacent p_21_9 p_22_9)
		(Adjacent p_21_9 p_21_8)
		(Adjacent p_21_12 p_20_12)
		(Adjacent p_21_14 p_20_14)
		(Adjacent p_21_14 p_22_14)
		(Adjacent p_22_2 p_21_2)
		(Adjacent p_22_2 p_23_2)
		(Adjacent p_22_4 p_21_4)
		(Adjacent p_22_4 p_23_4)
		(Adjacent p_22_9 p_21_9)
		(Adjacent p_22_9 p_23_9)
		(Adjacent p_22_9 p_22_10)
		(Adjacent p_22_10 p_22_9)
		(Adjacent p_22_14 p_21_14)
		(Adjacent p_22_14 p_23_14)
		(Adjacent p_23_1 p_23_2)
		(Adjacent p_23_2 p_22_2)
		(Adjacent p_23_2 p_24_2)
		(Adjacent p_23_2 p_23_3)
		(Adjacent p_23_2 p_23_1)
		(Adjacent p_23_3 p_23_4)
		(Adjacent p_23_3 p_23_2)
		(Adjacent p_23_4 p_22_4)
		(Adjacent p_23_4 p_23_3)
		(Adjacent p_23_6 p_24_6)
		(Adjacent p_23_9 p_22_9)
		(Adjacent p_23_9 p_24_9)
		(Adjacent p_23_12 p_24_12)
		(Adjacent p_23_14 p_22_14)
		(Adjacent p_23_14 p_24_14)
		(Adjacent p_24_2 p_23_2)
		(Adjacent p_24_2 p_25_2)
		(Adjacent p_24_6 p_23_6)
		(Adjacent p_24_6 p_25_6)
		(Adjacent p_24_6 p_24_7)
		(Adjacent p_24_7 p_24_6)
		(Adjacent p_24_9 p_23_9)
		(Adjacent p_24_9 p_24_10)
		(Adjacent p_24_10 p_25_10)
		(Adjacent p_24_10 p_24_9)
		(Adjacent p_24_12 p_23_12)
		(Adjacent p_24_12 p_24_13)
		(Adjacent p_24_13 p_25_13)
		(Adjacent p_24_13 p_24_14)
		(Adjacent p_24_13 p_24_12)
		(Adjacent p_24_14 p_23_14)
		(Adjacent p_24_14 p_24_13)
		(Adjacent p_25_1 p_26_1)
		(Adjacent p_25_1 p_25_2)
		(Adjacent p_25_2 p_24_2)
		(Adjacent p_25_2 p_25_3)
		(Adjacent p_25_2 p_25_1)
		(Adjacent p_25_3 p_26_3)
		(Adjacent p_25_3 p_25_4)
		(Adjacent p_25_3 p_25_2)
		(Adjacent p_25_4 p_25_5)
		(Adjacent p_25_4 p_25_3)
		(Adjacent p_25_5 p_26_5)
		(Adjacent p_25_5 p_25_6)
		(Adjacent p_25_5 p_25_4)
		(Adjacent p_25_6 p_24_6)
		(Adjacent p_25_6 p_25_5)
		(Adjacent p_25_10 p_24_10)
		(Adjacent p_25_10 p_26_10)
		(Adjacent p_25_13 p_24_13)
		(Adjacent p_25_13 p_26_13)
		(Adjacent p_26_1 p_25_1)
		(Adjacent p_26_3 p_25_3)
		(Adjacent p_26_5 p_25_5)
		(Adjacent p_26_5 p_27_5)
		(Adjacent p_26_8 p_27_8)
		(Adjacent p_26_8 p_26_9)
		(Adjacent p_26_9 p_27_9)
		(Adjacent p_26_9 p_26_10)
		(Adjacent p_26_9 p_26_8)
		(Adjacent p_26_10 p_25_10)
		(Adjacent p_26_10 p_26_11)
		(Adjacent p_26_10 p_26_9)
		(Adjacent p_26_11 p_26_12)
		(Adjacent p_26_11 p_26_10)
		(Adjacent p_26_12 p_26_13)
		(Adjacent p_26_12 p_26_11)
		(Adjacent p_26_13 p_25_13)
		(Adjacent p_26_13 p_26_14)
		(Adjacent p_26_13 p_26_12)
		(Adjacent p_26_14 p_26_13)
		(Adjacent p_27_5 p_26_5)
		(Adjacent p_27_5 p_28_5)
		(Adjacent p_27_5 p_27_6)
		(Adjacent p_27_6 p_27_7)
		(Adjacent p_27_6 p_27_5)
		(Adjacent p_27_7 p_28_7)
		(Adjacent p_27_7 p_27_8)
		(Adjacent p_27_7 p_27_6)
		(Adjacent p_27_8 p_26_8)
		(Adjacent p_27_8 p_27_9)
		(Adjacent p_27_8 p_27_7)
		(Adjacent p_27_9 p_26_9)
		(Adjacent p_27_9 p_28_9)
		(Adjacent p_27_9 p_27_8)
		(Adjacent p_28_1 p_29_1)
		(Adjacent p_28_1 p_28_2)
		(Adjacent p_28_2 p_28_3)
		(Adjacent p_28_2 p_28_1)
		(Adjacent p_28_3 p_28_4)
		(Adjacent p_28_3 p_28_2)
		(Adjacent p_28_4 p_28_5)
		(Adjacent p_28_4 p_28_3)
		(Adjacent p_28_5 p_27_5)
		(Adjacent p_28_5 p_28_4)
		(Adjacent p_28_7 p_27_7)
		(Adjacent p_28_9 p_27_9)
		(Adjacent p_28_9 p_28_10)
		(Adjacent p_28_10 p_28_11)
		(Adjacent p_28_10 p_28_9)
		(Adjacent p_28_11 p_28_12)
		(Adjacent p_28_11 p_28_10)
		(Adjacent p_28_12 p_28_13)
		(Adjacent p_28_12 p_28_11)
		(Adjacent p_28_13 p_28_14)
		(Adjacent p_28_13 p_28_12)
		(Adjacent p_28_14 p_28_13)
		(Adjacent p_29_1 p_28_1)
		(Adjacent p_29_1 p_30_1)
		(Adjacent p_30_1 p_29_1)
		(Adjacent p_30_1 p_30_2)
		(Adjacent p_30_2 p_30_3)
		(Adjacent p_30_2 p_30_1)
		(Adjacent p_30_3 p_30_4)
		(Adjacent p_30_3 p_30_2)
		(Adjacent p_30_4 p_30_5)
		(Adjacent p_30_4 p_30_3)
		(Adjacent p_30_5 p_30_6)
		(Adjacent p_30_5 p_30_4)
		(Adjacent p_30_6 p_30_7)
		(Adjacent p_30_6 p_30_5)
		(Adjacent p_30_7 p_30_8)
		(Adjacent p_30_7 p_30_6)
		(Adjacent p_30_8 p_30_9)
		(Adjacent p_30_8 p_30_7)
		(Adjacent p_30_9 p_30_10)
		(Adjacent p_30_9 p_30_8)
		(Adjacent p_30_10 p_30_11)
		(Adjacent p_30_10 p_30_9)
		(Adjacent p_30_11 p_30_12)
		(Adjacent p_30_11 p_30_10)
		(Adjacent p_30_12 p_30_13)
		(Adjacent p_30_12 p_30_11)
		(Adjacent p_30_13 p_30_14)
		(Adjacent p_30_13 p_30_12)
		(Adjacent p_30_14 p_30_13)
		(FoodAt p_17_6)
		(FoodAt p_21_1)
		(FoodAt p_21_4)
		(FoodAt p_21_6)
		(FoodAt p_21_8)
		(FoodAt p_21_12)
		(FoodAt p_22_4)
		(FoodAt p_22_10)
		(FoodAt p_23_1)
		(FoodAt p_23_6)
		(FoodAt p_23_12)
		(FoodAt p_24_6)
		(FoodAt p_24_7)
		(FoodAt p_24_12)
		(FoodAt p_26_1)
		(FoodAt p_26_3)
		(FoodAt p_26_14)
		(FoodAt p_28_7)
		(FoodAt p_28_13)
		(FoodAt p_28_14)
    )
   (:goal 
	( and  
		(not (FoodAt p_17_6))
		(not (FoodAt p_21_1))
		(not (FoodAt p_21_4))
		(not (FoodAt p_21_6))
		(not (FoodAt p_21_8))
		(not (FoodAt p_21_12))
		(not (FoodAt p_22_4))
		(not (FoodAt p_22_10))
		(not (FoodAt p_23_1))
		(not (FoodAt p_23_6))
		(not (FoodAt p_23_12))
		(not (FoodAt p_24_6))
		(not (FoodAt p_24_7))
		(not (FoodAt p_24_12))
		(not (FoodAt p_26_1))
		(not (FoodAt p_26_3))
		(not (FoodAt p_26_14))
		(not (FoodAt p_28_7))
		(not (FoodAt p_28_13))
		(not (FoodAt p_28_14))
	)
   )
)
