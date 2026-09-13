from django.core.management.base import BaseCommand
from main.models import Position


DUTIES = {
    'Carpenter': (
        "Cutting and processing wood according to technical drawings\n"
        "Assembling furniture frames and structural components\n"
        "Operating woodworking machinery (saws, planers, routers)\n"
        "Sanding, finishing, and preparing surfaces for coating\n"
        "Quality-checking finished parts and maintaining tools\n"
        "Following safety regulations in the workshop"
    ),
    'Carpetner': (   # на случай опечатки в БД
        "Cutting and processing wood according to technical drawings\n"
        "Assembling furniture frames and structural components\n"
        "Operating woodworking machinery (saws, planers, routers)\n"
        "Sanding, finishing, and preparing surfaces for coating\n"
        "Quality-checking finished parts and maintaining tools\n"
        "Following safety regulations in the workshop"
    ),
    'Customer Support Representative': (
        "Answering customer inquiries via phone, email, and chat\n"
        "Resolving complaints and providing product information\n"
        "Processing returns, exchanges, and warranty claims\n"
        "Documenting customer interactions in the CRM system\n"
        "Escalating complex issues to the appropriate department\n"
        "Maintaining a friendly and professional communication style"
    ),
    'Director': (
        "Developing and implementing company strategy\n"
        "Managing financial performance and budget planning\n"
        "Overseeing all departments and key business operations\n"
        "Negotiating with major partners, suppliers, and clients\n"
        "Representing the company at official events and exhibitions\n"
        "Making high-level decisions on investments and expansion"
    ),
    'Furniture Assembler': (
        "Assembling furniture pieces according to assembly instructions\n"
        "Using hand and power tools safely and efficiently\n"
        "Checking all parts for defects before assembly\n"
        "Applying fittings, hinges, handles, and hardware\n"
        "Packaging finished furniture for delivery\n"
        "Maintaining a clean and organized workspace"
    ),
    'Logistics Coordinator': (
        "Planning and coordinating shipments and deliveries\n"
        "Communicating with transport companies and drivers\n"
        "Tracking orders and updating delivery status\n"
        "Preparing shipping documents and waybills\n"
        "Optimizing delivery routes and reducing transportation costs\n"
        "Resolving delivery issues and handling returns"
    ),
    'Manager': (
        "Supervising daily operations of the department\n"
        "Assigning tasks and monitoring team performance\n"
        "Handling client inquiries and preparing commercial offers\n"
        "Coordinating with production and logistics departments\n"
        "Preparing reports for senior management\n"
        "Training and mentoring new employees"
    ),
    'Quality Control Specialist': (
        "Inspecting raw materials and finished products\n"
        "Checking compliance with technical specifications and standards\n"
        "Documenting defects and preparing quality reports\n"
        "Investigating causes of defects and proposing improvements\n"
        "Conducting regular audits of production processes\n"
        "Ensuring adherence to ISO and safety standards"
    ),
    'SMM': (
        "Managing social media accounts (Instagram, Facebook, TikTok)\n"
        "Creating, scheduling, and publishing content\n"
        "Running targeted advertising campaigns\n"
        "Analyzing engagement metrics and audience growth\n"
        "Coordinating with designers, photographers, and copywriters\n"
        "Monitoring competitors and trending topics"
    ),
    'Sales Manager': (
        "Finding and attracting new clients\n"
        "Conducting negotiations and preparing commercial offers\n"
        "Closing deals and processing sales contracts\n"
        "Maintaining long-term relationships with existing clients\n"
        "Achieving monthly and quarterly sales targets\n"
        "Reporting sales results and market feedback"
    ),
    'Storekeeper': (
        "Receiving and inspecting incoming materials and goods\n"
        "Recording stock movements in the warehouse system\n"
        "Organizing storage and maintaining order in the warehouse\n"
        "Issuing materials to production upon request\n"
        "Conducting regular inventory checks and audits\n"
        "Ensuring compliance with safety and storage regulations"
    ),
}


class Command(BaseCommand):
    help = 'Fill position descriptions with predefined duties'

    def handle(self, *args, **options):
        updated = 0
        skipped = []

        for position in Position.objects.all():
            duties = DUTIES.get(position.name)
            if duties:
                position.description = duties
                position.save()
                updated += 1
                self.stdout.write(f'Filled: {position.name}')
            else:
                skipped.append(position.name)

        if skipped:
            self.stdout.write(self.style.WARNING(
                f'Skipped (no duties found): {", ".join(skipped)}'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'Done. Updated {updated} positions.'
        ))