# aws_tagging_service

1. Run dry-run to create change set file tag_changes.csv by running
    python main_tagging.py dry_run

2. Audit the changes and modify if needed

3. Apply the final changeset by running
    python main_tagging.py

4. Delete the tag_changes.csv before the next run


# Note
 Only tags with prefix trhc will be targetted for valideation and modification
