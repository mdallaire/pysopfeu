"""Console script for pysopfeu."""

import click
import json
from pysopfeu import wms_to_json, construct_wms_url

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option('--lat', type=float, help='Latitude in EPSG:4326')
@click.option('--lon', type=float, help='Longitude in EPSG:4326')
@click.option('--width', type=int, default=10, help='Width of the image (default: 10)')
@click.option('--height', type=int, default=10, help='Height of the image (default: 10)')
@click.option('--output', type=click.Path(), help='Output file to save the JSON data')
@click.option('--show-url', is_flag=True, help='Show the generated WMS URL and exit')
def main(lat, lon, width, height, output, show_url):

    # If no parameters are provided, display the introductory message and help
    if not any([lat, lon, output, show_url]):
        click.echo("pysopfeu")
        click.echo("=" * len("pysopfeu"))
        click.echo("Bibliothèque pour accéder aux données de la SOPFEU publiées sur Données Québec")
        click.echo("\nUtilisation :")
        click.echo(main.get_help(click.get_current_context()))
        return

    if lat is None or lon is None:
        click.echo("Veuillez fournir les options --lat et --lon.", err=True)
        return

    # If --show-url is provided, generate and display the WMS URL
    if show_url:
        url = construct_wms_url(lat, lon, width, height)
        click.echo(f"Generated WMS URL:\n{url}")
        return

    try:
        # Call the wms_to_json function
        json_data = wms_to_json(lat, lon, width, height)

        if output:
            # Save the output to a file
            with open(output, 'w', encoding='utf-8') as f:
                f.write(json_data)
            click.echo(f"Les données ont été enregistrées dans {output}")
        else:
            # Print the JSON data
            click.echo(json_data)

    except Exception as e:
        click.echo(f"Une erreur s'est produite : {e}", err=True)

if __name__ == "__main__":
    main()  # pragma: no cover
