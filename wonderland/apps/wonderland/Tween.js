export class Tween {
  static LINEAR = linear
  static QUAD_IN_OUT = quadraticInOut
  static QUAD_OUT = quadraticOut

  constructor(start) {
    this.start = start
    this.value = {}
    this.steps = []
    this.keys = []
    this.loopEnabled = false
    this.duration = 0
  }

  to(value, duration, easing) {
    const prevStep = this.steps[this.steps.length - 1]
    const startsAt = prevStep?.endsAt || 0
    const endsAt = startsAt + duration
    const from = prevStep?.to || this.start
    const step = {
      from,
      to: value,
      startsAt,
      endsAt,
      duration,
      easing,
    }
    this.steps.push(step)
    this.duration += duration
    return this
  }

  wait(duration) {
    const prevStep = this.steps[this.steps.length - 1]
    const startsAt = prevStep?.endsAt || 0
    const endsAt = startsAt + duration
    const value = prevStep?.to || this.start
    const step = {
      from: value,
      to: value,
      startsAt,
      endsAt,
      duration,
      easing: noEasing,
    }
    this.steps.push(step)
    this.duration += duration
    return this
  }

  loop() {
    this.loopEnabled = true
    return this
  }

  set(time) {
    if (time < 0) time = 0
    if (this.loopEnabled) time = time % this.duration
    let step
    for (const _step of this.steps) {
      if (time >= _step.startsAt) {
        step = _step
      }
    }
    if (!step) {
      return console.warn('no step', time)
    }
    let alpha = (time - step.startsAt) / step.duration
    if (alpha > 1) alpha = 1
    const ease = step.easing(alpha)
    for (const key in step.to) {
      this.value[key] = step.from[key] + ( (step.to[key] - step.from[key]) * ease) // prettier-ignore
    }
  }
}

function noEasing() {
  return 1
}

function quadraticInOut(amount) {
  if ((amount *= 2) < 1) {
    return 0.5 * amount * amount
  }
  return -0.5 * (--amount * (amount - 2) - 1)
}

function quadraticOut(amount) {
  return amount * (2 - amount)
}

function linear(amount) {
  return amount
}
