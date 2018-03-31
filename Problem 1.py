from enum import Enum
import numpy as np
import scr.SamplePathClasses as PathCls
import scr.StatisticalClasses as Stat


class HealthStat(Enum):
    """ health status of patients  """
    ALIVE = 1
    DEAD = 0


class Patient:
    def __init__(self, id, mortality_prob):
        """ initiates a patient
        :param id: ID of the patient
        :param mortality_prob: probability of death during a time-step (must be in [0,1])
        """
        self._id = id
        self._rnd = np.random       # random number generator for this patient
        self._rnd.seed(self._id)    # specifying the seed of random number generator for this patient

        self._mortalityProb = mortality_prob
        self._healthState = HealthStat.ALIVE  # assuming all patients are alive at the beginning
        self._survivalTime = 0

    def simulate(self, n_time_steps):
        """ simulate the patient over the specified simulation length """

        t = 0  # simulation current time

        # while the patient is alive and simulation length is not yet reached
        while self._healthState == HealthStat.ALIVE and t < n_time_steps:
            # determine if the patient will die during this time-step
            if self._rnd.sample() < self._mortalityProb:
                self._healthState = HealthStat.DEAD
                self._survivalTime = t + 1  # assuming deaths occurs at the end of this period

            # increment time
            t += 1

    def get_survival_time(self):
        """ returns the patient survival time """

        # return survival time only if the patient has died
        if self._healthState == HealthStat.DEAD:
            return self._survivalTime
        else:
            return None


class Cohort:
    def __init__(self, id, pop_size, mortality_prob):
        """ create a cohort of patients
        :param id: cohort ID
        :param pop_size: population size of this cohort
        :param mortality_prob: probability of death for each patient in this cohort over a time-step (must be in [0,1])
        """
        self._initialPopSize = pop_size # initial population size
        self._patients = []      # list of patients
        self._survivalTimes = []    # list to store survival time of each patient

        # populate the cohort
        for i in range(pop_size):
            # create a new patient (use id * pop_size + n as patient id)
            patient = Patient(id * pop_size + i, mortality_prob)
            # add the patient to the cohort
            self._patients.append(patient)

    def simulate(self, n_time_steps):
        """ simulate the cohort of patients over the specified number of time-steps
        :param n_time_steps: number of time steps to simulate the cohort
        :returns simulation outputs from simulating this cohort
        """

        # simulate all patients
        for patient in self._patients:
            # simulate
            patient.simulate(n_time_steps)
            # record survival time
            value = patient.get_survival_time()
            if not (value is None):
                self._survivalTimes.append(value)

        # return cohort outcomes for this simulated class
        return CohortOutcomes(self)

    def get_survival_times(self):
        """ :returns the survival times of the patients in this cohort"""
        return self._survivalTimes

    def get_initial_pop_size(self):
        """ :returns the initial population size of this cohort"""
        return self._initialPopSize


class CohortOutcomes:
    def __init__(self, simulated_cohort):
        """ extracts outcomes of a simulated cohort
        :param simulated_cohort: a cohort after being simulated"""

        self._simulatedCohort = simulated_cohort

        # summary statistics on survival times
        self._sumStat_patientSurvivalTimes = \
            Stat.SummaryStat('Patient survival times', self._simulatedCohort.get_survival_times())

    def get_ave_survival_time(self):
        """ returns the average survival time of patients in this cohort """
        return self._sumStat_patientSurvivalTimes.get_mean()

    def get_CI_survival_time(self, alpha):
        """
        :param alpha: confidence level
        :return: t-based confidence interval
        """
        return self._sumStat_patientSurvivalTimes.get_t_CI(alpha)

    def get_survival_curve(self):
        """ returns the sample path for the number of living patients over time """

        # find the initial population size
        n_pop = self._simulatedCohort.get_initial_pop_size()
        # sample path (number of alive patients over time)
        n_living_patients = PathCls.SamplePathBatchUpdate('# of living patients', 5, n_pop)

        # record the times of deaths
        for obs in self._simulatedCohort.get_survival_times():
            n_living_patients.record(time=obs, increment=-1)

        return n_living_patients

        after5 = n_living_patients / n_pop

        print('Percentage of living patients after 5 years:', after5 )

    def get_survival_times(self):
        """ :returns the survival times of the patients in this cohort"""
        return self._simulatedCohort.get_survival_times()

