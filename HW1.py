if __name__ == '__main__':
    from atmosphere import Atmosphere

    """
    Define the different regions of the standard atmosphere
    """
    regions = [
        (0, -0.0065),
        (11000, 0),
        (25000, 0.003)
    ]  # altitude, lapse rate
    """
    Define constants at sea level
    """
    t_sl = 288.16  # K
    p_sl = 101325  # Pa
    rho_sl = 1.2250  # kg/m^3

    # Initialize atmosphere object
    atm = Atmosphere(regions, t_sl, p_sl, rho_sl)

    # Generate data at requested altitudes
    altitudes = []
    temps = []
    densities = []
    visc_coeffs = []
    for i in range(0, 25001, 500):
        altitudes.append(i)
        temps.append(atm.temperature_at(i))
        densities.append(atm.density_at(i))
        visc_coeffs.append(atm.viscosity_coeff_at(i))


    # Reformat as Strings
    alt_str = ['%d' % i for i in altitudes]
    temp_str = ['%.4f' % i for i in temps]
    dens_str = ['%.4f' % i for i in densities]

    data = [[a, t, rho] for a, t, rho in zip(alt_str, temp_str, dens_str)]

    # Start working with matplotlib to view data in a table
    from matplotlib import pyplot as plt
    from matplotlib.font_manager import FontProperties

    fig, axs = plt.subplots(1, 1)
    fig.set_size_inches(11, 8.5)

    col_labels = ('Altitude, h [m]', 'Temp., T [K]', 'Density, \N{GREEK SMALL LETTER RHO} [kg/m\N{SUPERSCRIPT THREE}]')
    axs.axis('auto')
    axs.axis('off')

    table = axs.table(cellText=data, colLabels=col_labels, loc='center', cellLoc='center')
    # make headers bold
    for (row, col), cell in table.get_celld().items():
        if (row == 0) or (col == -1):
            cell.set_text_props(fontproperties=FontProperties(weight='bold'))

    # show plot
    plt.show()
    # save as PNG file
    fig.savefig('StandardAtmosphere.png', dpi=200, bbox_inches='tight', pad_inches=0.5)

    # -------------------------------------------------------------------
    plt.cla()
    plt.clf()
    plt.semilogy(altitudes, densities)
    plt.title('Density vs. Altitude')
    plt.xlabel('Altitude [m]')
    plt.ylabel('Density [kg/m\N{SUPERSCRIPT THREE}]')
    plt.show()
    # -------------------------------------------------------------------
    plt.cla()
    plt.clf()
    plt.plot(temps, altitudes)
    plt.title('Altitude vs. Temperature')
    plt.xlabel('Temperature [K]')
    plt.ylabel('Altitude [m]')
    plt.show()
    # -------------------------------------------------------------------
    plt.cla()
    plt.clf()
    plt.plot(temps, visc_coeffs)
    plt.title('Viscosity Coefficient vs. Temperature')
    plt.xlabel('Temperature [K]')
    plt.ylabel('Viscosity Coefficient [kg/(m*s)]')
    plt.show()
