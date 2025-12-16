"""

from analyser.wer.wer_io import WERIO
from analyser.wer.wer_preprocessor import WERPreprocessor
from analyser.wer.wer_calculator import WERCalculator
from pathlib import Path

output_dir = "Output"
ref_txt = Path("Output/a.txt")
hyp_json = Path("Output/a.json")
# output_dir = "Output"
# ref_txt = Path("Dataset/Ses01F_impro01/transcript_norm.txt")
# hyp_json = Path("Output/result.json")

# IO
io = WERIO()
ref_text = io.load_reference(ref_txt)
hyp_text = io.load_hypothesis_from_json(hyp_json)

# Preprocess
prep = WERPreprocessor()
ref_norm = prep.normalize_reference(ref_text)
hyp_norm = prep.normalize_hypothesis(hyp_text)

# Calculate
wer_calc = WERCalculator(output_dir)
wer_calc.load_inputs(ref_norm, hyp_norm)
wer_calc.calculate()
wer_calc.save_result()
"""
def calculate():
        """
        Calculate WER using edit distance.
        """
        a = 0
        ref_words = ["excuse","me","please"]
        print(" ref_words ",ref_words)

        hyp_words = ["excuse","me"]
        print(" hyp_words ",hyp_words)
        N = len(ref_words)
        if N ==0:
            print("input invalid")
            return
        #DP edit distance
        dp = [[0] *(len(hyp_words)+1)for _ in range(len(ref_words)+1)]
        print("your dp is : ", dp)
        for i in range(len(ref_words)+1):
            dp[i][0] = i
        print()
        print(dp)
        for j in range(len(hyp_words)+1):
            dp[0][j] = j

        print()
        print(dp)

        for i in range (1,len(ref_words)+1):
            for j in range(1,len(hyp_words)+1):
                if ref_words[i-1] ==hyp_words[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1+min(
                        dp[i-1][j],     #deletion
                        dp[i][j-1],     #insertion
                        dp[i-1][j-1]    #substitution
                        )
            print()
            print(dp)
            a = dp[len(ref_words)][len(hyp_words)]/N
            print("wer =" ,a)
calculate()
