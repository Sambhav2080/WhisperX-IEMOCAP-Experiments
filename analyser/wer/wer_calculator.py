from analyser.base.analyser_base import AnalyserBase


class WERCalculator(AnalyserBase):
    """
    Calculates Word Error Rate.
    """

    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.reference_text = None
        self.hypothesis_text = None
        self.wer_value = None

    def load_inputs(self, reference_text: str, hypothesis_text: str):
        self.reference_text = reference_text
        self.hypothesis_text = hypothesis_text

    def preprocess(self):
        """
        Preprocessing is done outside (WERPreprocessor).
        This method exists to respect base interface.
        """
        pass

    def calculate(self):
        """
        Calculate WER using edit distance.
        """
        ref_words = self.reference_text.split()

        hyp_words = self.hypothesis_text.split()
        N = len(ref_words)
        if N ==0:
            self.wer_value = 0.0
            return
        #DP edit distance
        dp = [[0] *(len(hyp_words)+1)for _ in range(len(ref_words)+1)]
        print("your dp is : ", dp)
        for i in range(len(ref_words)+1):
            dp[i][0] = i
        for j in range(len(hyp_words)+1):
            dp[0][j] = j


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
            self.wer_value = dp[len(ref_words)][len(hyp_words)]/N
            return self.wer_value
    
