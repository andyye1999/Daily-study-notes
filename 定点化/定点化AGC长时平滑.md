
```c
void agc(
  Word16 *sig_in,   /* (i)     : postfilter input signal  */
  Word16 *sig_out,  /* (i/o)   : postfilter output signal */
  Word16 l_trm      /* (i)     : subframe size            */
)
{
  static Word16 past_gain=4096;         /* past_gain = 1.0 (Q12) */
  Word16 i, exp;
  Word16 gain_in, gain_out, g0, gain;                     /* Q12 */
  Word32 s;

  Word16 signal[L_SUBFR];

  /* calculate gain_out with exponent */

  for(i=0; i<l_trm; i++)
    signal[i] = shr(sig_out[i], 2);

  s = 0;
  for(i=0; i<l_trm; i++)
    s = L_mac(s, signal[i], signal[i]);

  if (s == 0) {
    past_gain = 0;
    return;
  }
  exp = sub(norm_l(s), 1);
  gain_out = round(L_shl(s, exp));

  /* calculate gain_in with exponent */

  for(i=0; i<l_trm; i++)
    signal[i] = shr(sig_in[i], 2);

  s = 0;
  for(i=0; i<l_trm; i++)
    s = L_mac(s, signal[i], signal[i]);

  if (s == 0) {
    g0 = 0;
  }
  else {
    i = norm_l(s);
    gain_in = round(L_shl(s, i));
    exp = sub(exp, i);

   /*---------------------------------------------------*
    *  g0(Q12) = (1-AGC_FAC) * sqrt(gain_in/gain_out);  *
    *---------------------------------------------------*/

    s = L_deposit_l(div_s(gain_out,gain_in));   /* Q15 */
    s = L_shl(s, 7);           /* s(Q22) = gain_out / gain_in */
    s = L_shr(s, exp);         /* Q22, add exponent */

    /* i(Q12) = s(Q19) = 1 / sqrt(s(Q22)) */
    s = Inv_sqrt(s);           /* Q19 */
    i = round(L_shl(s,9));     /* Q12 */

    /* g0(Q12) = i(Q12) * (1-AGC_FAC)(Q15) */
    g0 = mult(i, AGC_FAC1);       /* Q12 */
  }

  /* compute gain(n) = AGC_FAC gain(n-1) + (1-AGC_FAC)gain_in/gain_out */
  /* sig_out(n) = gain(n) sig_out(n)                                   */

  gain = past_gain;
  for(i=0; i<l_trm; i++) {
    gain = mult(gain, AGC_FAC);
    gain = add(gain, g0);
    sig_out[i] = extract_h(L_shl(L_mult(sig_out[i], gain), 3));
  }
  past_gain = gain;

  return;
}
```