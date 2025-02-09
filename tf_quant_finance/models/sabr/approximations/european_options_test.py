# Lint as: python3
# Copyright 2021 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tests for Sabr Approximations of European Option prices."""

from absl.testing import parameterized

import numpy as np
import tensorflow.compat.v2 as tf

import tf_quant_finance as tff

# Helper aliases.
NORMAL = tff.models.sabr.approximations.SabrImpliedVolatilityType.NORMAL
LOGNORMAL = tff.models.sabr.approximations.SabrImpliedVolatilityType.LOGNORMAL


class SabrApproximationEuropeanOptionsTest(parameterized.TestCase,
                                           tf.test.TestCase):
  """Tests for SABR approximations to implied volatility."""

  def test_european_option_docstring_example(self):
    prices = tff.models.sabr.approximations.european_option_price(
        forwards=np.array([100.0, 110.0]),
        strikes=np.array([90.0, 100.0]),
        expiries=np.array([0.5, 1.0]),
        is_call_options=np.array([True, False]),
        alpha=3.2,
        beta=0.2,
        nu=1.4,
        rho=0.0005,
        dtype=tf.float64)

    prices = self.evaluate(prices)
    self.assertAllClose(prices, [10.41244961, 1.47123225])

  def test_european_option_normal(self):
    prices = tff.models.sabr.approximations.european_option_price(
        forwards=np.array([100.0, 110.0]),
        strikes=np.array([90.0, 100.0]),
        expiries=np.array([0.5, 1.0]),
        is_call_options=np.array([True, False]),
        alpha=3.2,
        beta=0.2,
        nu=1.4,
        rho=0.0005,
        volatility_type=NORMAL,
        dtype=tf.float64)

    prices = self.evaluate(prices)
    self.assertAllClose(prices, [10.412692, 1.472544])

  @parameterized.product(
      (
          # Generic example, with tensor values, including at-the-money case and
          # at-expiry case.
          {
              'strikes':
                  np.array([[130.0, 140.0, 150.0], [130.0, 140.0, 150.0]]),
              'forwards':
                  140.0,
              'expiries': [[0.0], [1.0]],
              'alpha': [[0.25], [0.5]],
              'beta': [[0.33], [0.66]],
              'nu': [[1.0], [2.0]],
              'rho': [[0.001], [-0.001]],
          },),
      is_call=(True, False, [[True], [False]], [[False], [True]]),
      vol_type=(NORMAL, LOGNORMAL),
  )
  def test_european_option_differentiable(self, strikes, forwards, expiries,
                                          alpha, beta, nu, rho, is_call,
                                          vol_type):
    dtype = tf.float64

    forwards = tf.convert_to_tensor(forwards, dtype=dtype)
    strikes = tf.convert_to_tensor(strikes, dtype=dtype)
    expiries = tf.convert_to_tensor(expiries, dtype=dtype)
    alpha = tf.convert_to_tensor(alpha, dtype=dtype)
    beta = tf.convert_to_tensor(beta, dtype=dtype)
    rho = tf.convert_to_tensor(rho, dtype=dtype)
    nu = tf.convert_to_tensor(nu, dtype=dtype)
    is_call = tf.convert_to_tensor(is_call)

    with tf.GradientTape(persistent=True) as tape:
      tape.watch([forwards, strikes, expiries, alpha, beta, rho, nu])
      price = tff.models.sabr.approximations.european_option_price(
          forwards=forwards,
          strikes=strikes,
          expiries=expiries,
          is_call_options=is_call,
          alpha=alpha,
          beta=beta,
          rho=rho,
          nu=nu,
          volatility_type=vol_type,
          dtype=dtype)
      grad = tape.gradient(
          target=price,
          sources=[forwards, strikes, expiries, alpha, beta, rho, nu])

    grad = self.evaluate(grad)
    self.assertTrue(all(np.all(np.isfinite(x)) for x in grad))


if __name__ == '__main__':
  tf.test.main()
