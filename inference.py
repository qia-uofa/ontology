from time import time

from api import next_token_p, chat, MODEL_URLS
import os

class DistributionInference:
    def prompter(self, proposition):
        return f'''Determine the True/False value of the next occurring proposition:

The given proposition:

{proposition}

4. If you are genuinely uncertain, think about the negation of the given proposition:

{~ proposition}

If both are uncertain, then the proposition is in a superposition of True and False with a probability $p$. Evaluate $p$ and sample a True/False value ~ Ber(p)

The output must strictly be a single string "True" or "False", with the first letter capitalized.'''

    def classifier(self, distribution):
        yes = ['true', 'True', 'TRUE']
        no = ['false', 'False', 'FALSE']
        a, b = 0, 0
        for key,val in distribution.items():
            for y in yes:
                if y in key:
                    a += val
            for n in no:
                if n in key:
                    b += val
        return a/(a+b)

    def generator(self, prompt):
        return next_token_p(prompt, api_key=os.getenv('OPENAI_API'))

    def ontology(self, proposition, condition=None):
        if condition is None:
            return self.classifier(
                self.generator(
                    self.prompter(
                        proposition
            )))
        else:
            return self.ontology(
                condition & proposition
            ) / self.ontology(
                condition
            )


import re
class MonteCarloInference:
    def __init__(
            self, 
            prompter=None,
            classifier=None,
            sample_size = 100, 
            enable_log=True, 
            log_path='./log.md', 
            model='gpt-5.5-pro', 
            api_key_var='OPENAI_API',
            wait_time=0
        ):
        self.model = model
        self.api_key_var = api_key_var
        self.sample_size = sample_size
        self.enable_log = enable_log
        self.log_path = log_path
        self.counter = 0
        self.classifier = classifier if classifier else lambda samples: self._classifier(samples)
        self.prompter = prompter if prompter else lambda proposition: self._prompter(proposition)
        self.wait_time = wait_time

    def log(self, *log_strings):
        if self.enable_log:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write('\n\n'.join(log_strings))
                f.write('\n\n')

    def _prompter(self, proposition):
        return f'''Determine the True/False value of the next occurring proposition:

1. Think through the problem step by step, considering relevant evidence and perspectives.
2. After reasoning, give your final answer strictly using one of these tags:
    <answer>True</answer> or <answer>False</answer>
3. If you change your mind, write a new answer tag. Only the last answer tag will be counted.

The given proposition:

{proposition}

4. If you are genuinely uncertain about the proposition, or there are not enough information to evaluate the proposition, write an answer anyways without thinking too much.
5. Remember that a proposition is not simply true because it\'s likely to be true.'''

    def _classifier(self, samples):
        pattern = r'<answer>(True|False)</answer>'
        true, false = 0, 0
        for sample in samples:
            matches = re.findall(pattern, sample, re.IGNORECASE)
            if matches:
                last_answer = matches[-1].strip().lower()
                if last_answer == 'true':
                    true += 1
                else:
                    false += 1
        p = true / (true + false)
        self.log(
            '## Conclusion',
            f'With {true} samples yieling True and {false} samples yieling false, '
            + f'we conclude that the ontology of the generator about the inferred proposition ~ Ber({p}). '
        )
        return p

    def generator(self, prompt):
        results = []
        self.log('## Samples')
        i = 0
        while i < self.sample_size:
            self.log(f'### Sample {i+1}')
            try:
                result = chat(
                    prompt,
                    model=self.model,
                    api_key=os.getenv(self.api_key_var)
                )
                self.log(f'```\n{result}\n```')
                results.append(result)      
                i += 1
            except Exception as e: 
                self.log(f'```\n{e}\n```')
                time.sleep(1)
            time.sleep(self.wait_time)
        return results

    def ontology(self, proposition, condition=None):
        if condition is None:
            self.log('# Ontology')
            self.log(
                '## Proposition',
                f'```\n{proposition}\n```'
            )

            alpha = self.prompter(proposition)

            self.log(
                '## Prompt',
                f'```\n{alpha}\n```'
            )

            beta = self.generator(alpha)
            p = self.classifier(beta)

            return p
        else:
            p = self.ontology(condition)
            if p == 0:
                return 0
            else:
                return self.ontology(condition & proposition) / p