#!/usr/bin/env python

"""
A script to detect and delete all Model Armor templates in a given project.

This script is for cleanup purposes and should be used with caution. It will
permanently delete the resources it finds.

Usage:
    python cleanup_templates.py --project_id "your-gcp-project-id --location "us-central1"
"""

import argparse
import sys
from google.cloud import modelarmor_v1


def cleanup_project_templates(project_id: str, location: str):
    """
    Initializes the Model Armor client, lists all templates, and deletes them.

    Args:
        project_id: The ID of the Google Cloud project to clean up.
    """

    try:
        client = modelarmor_v1.ModelArmorClient(transport="rest", client_options={"api_endpoint": f"modelarmor.{location}.rep.googleapis.com"})
        print("Client initialized successfully.")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
    
    print(f"--- Starting Model Armor Cleanup for Project: {project_id} ---")

    try:

       #Initialise request argument(s)
        request = modelarmor_v1.ListTemplatesRequest(
            parent=f"projects/{project_id}/locations/{location}"
        )

        # 2. Detect (list) all existing templates in the project
        print("\nFetching all existing templates...")
        templates_to_delete = client.list_templates(request=request)
        #print(templates_to_delete)

        if not templates_to_delete:
            print("No Model Armor templates found in this project. Nothing to do.")
            print("--- Cleanup Complete ---")
            return


        # 3. Iterate through the list and delete each template
        print("\nBeginning deletion process...")
        for template in templates_to_delete:
            try:
                #print(template)
                print(f"Deleting template: '{template.name}'...")
                # The delete method likely takes the template's name or ID
                request = modelarmor_v1.DeleteTemplateRequest(
                        name = template.name,
                )
                response = client.delete_template(request=request)
                print(f"  Successfully deleted '{template.name}'.")
            except Exception as e:
                print(f"  ERROR: Failed to delete '{template.name}'. Reason: {e}")

    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("Aborting cleanup operation.")

    finally:
        print("\n--- Cleanup Complete ---")


if __name__ == "__main__":
    # Set up an argument parser to accept the project ID from the command line
    parser = argparse.ArgumentParser(
        description="Find and delete all Model Armor templates in a Google Cloud project."
    )
    parser.add_argument(
        "--project_id",
        type=str,
        required=True,
        help="The Google Cloud project ID containing the templates to delete.",
    )

    parser.add_argument(
        "--location",
        type=str,
        required=True,
        help="The Google Cloud location  containing the templates to delete.",
    )

    args = parser.parse_args()
    cleanup_project_templates(args.project_id, args.location)
