#!/usr/bin/env python
# coding=utf-8

import numpy as np
import matplotlib.pyplot as plt
from lande_factor import DataGenerator, Lande, events_top, events_bot
from scipy.constants import e, physical_constants
from multiprocessing import Pool


def perform_fit(gen_pars):
    limits = (2, 13)
    pars_top = gen_pars[0]
    pars_bot = gen_pars[1]
    top_gen = DataGenerator(events_top, limits, size=int(1e6), **pars_top)
    bot_gen = DataGenerator(events_bot, limits, size=int(4e5), **pars_bot)
    data = np.array([top_gen.gen_data(), bot_gen.gen_data()])
    lande = Lande(data, limits)
    starting_values = {'omega': 3, 'delta': np.pi, 'a_bar_top': 1e-4, 'a_bar_bot': 1e-4}
    par_limits = {'a_bar_top': (1e-20, 1), 'a_bar_bot': (1e-20, 1)}
    lande.do_fit(starting_values=starting_values, par_limits=par_limits, pre_fit=True)
    return np.array([lande.fit_multi.parameter_values, lande.fit_multi.parameter_errors])


if __name__ == '__main__':
    random = np.random.RandomState(18560472)  # fix seed for reproduction
    tau = 2.1969811  # mean decay time in micro seconds
    g_ref = 2.0023318418  # lande factor of the myon
    m = physical_constants["muon mass"][0]
    magnetic_fields = np.array([3.5, 5])*1e-3  # magnetic fields in T
    frequencies = g_ref * e * magnetic_fields / (2 * m)
    a_bar = np.linspace(0.01, 0.1, num=10)
    p = Pool(processes=4)
    for omega in frequencies:
        gen_pars = []
        for a in a_bar:
            delta = random.rand()*2*np.pi  # generate random phase delay in the interval (0, 2*pi)
            gen_pars_top = {'tau': tau, 'k_top': 0.8, 'a_bar_top': a/10, 'omega': omega * 1e-6,
                            'delta': delta, 'f_top': 2e-2}
            gen_pars_bot = {'tau': tau, 'k_bot': 0.7, 'a_bar_bot': a, 'omega': omega * 1e-6,
                            'delta': delta, 'f_bot': 2e-2}
            gen_pars.append([gen_pars_top, gen_pars_bot])
        fit_results = np.array(p.map(perform_fit, gen_pars))
        fig, ax = plt.subplots()
        ax.errorbar(a_bar, fit_results[:, 0, 3], yerr=fit_results[:, 1, 3], fmt='o', label='Fit Values')
        ax.plot(a_bar, np.ones_like(a_bar)*omega*1e-6, 'r--', label=r'Expected $\omega$')
        ax.set_ylabel(r'$\omega$ [MHz]')
        ax.set_xlabel(r'Generator value for $\bar{A}_1$')
        ax.legend()
        plt.show()