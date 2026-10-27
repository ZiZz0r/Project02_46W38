import numpy as np


def load_wind_data(filename):
    """
    Load wind data from a text file.

    Parameters:½½½½
        filename: Path to the wind data file.

    Returns:
        time: Array of time values in seconds.
        wind_speed: Array of wind speeds in m/s.
    """
    wind_data = np.loadtxt(filename, skiprows=1)

    time = wind_data[:, 0]  # Time values, column 0
    wind_speed = wind_data[:, 1]  # Wind speed values, column 1

    return time, wind_speed


def calculate_CT(wind_speed, ct_data):
    """
    Find the thrust coefficient using the mean wind speed.

    Parameters:
        wind_speed: Array of wind speed values.
        ct_data: Lookup table containing wind speeds and CT values.

    Returns:
        ct_interpolated: Interpolated thrust coefficient.
    """
    mean_wind_speed = np.mean(wind_speed)

    ct_interpolated = np.interp(
        mean_wind_speed, ct_data[:, 0], ct_data[:, 1]
    )

    return ct_interpolated


def create_system_matrices(mb, mn, mh, mt, c1, c2, k1, k2):
    """
    Create the mass, damping and stiffness matrices for Turbie.

    Parameters:
        mb: Mass of one blade.
        mn: Mass of nacelle.
        mh: Mass of hub.
        mt: Mass of tower.
        c1, c2: Damping coefficients.
        k1, k2: Stiffness coefficients.

    Returns:
        M: Mass matrix.
        C: Damping matrix.
        K: Stiffness matrix.
    """
    m1 = 3 * mb
    m2 = mn + mh + mt

    M = np.array([
        [m1, 0],
        [0, m2]
    ])

    C = np.array([
        [c1, -c1],
        [-c1, c1 + c2]
    ])

    K = np.array([
        [k1, -k1],
        [-k1, k1 + k2]
    ])

    return M, C, K


def turbine_motion(t, y, M, C, K, wind_at_time, rho, CT, A):
    """
    Calculate the state derivatives of the 2DOF turbine model.

    Parameters:
        t: Current simulation time.
        y: State vector [x1, x2, v1, v2].
        M: Mass matrix.
        C: Damping matrix.
        K: Stiffness matrix.
        wind_at_time: Function returning wind speed at time t.
        rho: Air density.
        CT: Thrust coefficient.
        A: Rotor swept area.

    Returns:
        Array containing [v1, v2, a1, a2], where a1 and a2
        are the accelerations of the blades and tower.
    """
    x1, x2, v1, v2 = y

    x = np.array([x1, x2])
    v = np.array([v1, v2])

    u = wind_at_time(t)
    u_rel = u - v1

    F_aero = 0.5 * rho * A * CT * u_rel * abs(u_rel)
    F = np.array([F_aero, 0])

    net_force = F - C @ v - K @ x
    a = np.linalg.solve(M, net_force)

    return np.array([v1, v2, a[0], a[1]])
