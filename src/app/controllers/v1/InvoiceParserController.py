import json
import os
import time
from datetime import datetime, UTC

from flask import Blueprint, request, jsonify, current_app, Response
from google.cloud import tasks_v2
from werkzeug.exceptions import BadRequest

from ...config.CloudTasksConfiguration import get_cloud_tasks_queue_path
from ...models.dto.response.v1.JobStatus import JobStatus
from ...services.ParserService import ParserService
from typing import List
from werkzeug.datastructures import FileStorage
import uuid
from ...services import services

invoice_bp = Blueprint('invoice', __name__)


# @invoice_bp.route('/process-pdfs-async', methods=['POST'])
# def process_pdfs_async():
#     try:
#         if 'pdfs' not in request.files:
#             raise BadRequest('No files provided')
#
#         files: List[FileStorage] = request.files.getlist('pdfs')
#
#         if not files:
#             raise BadRequest('No files selected')
#
#         # Validate files
#         for file in files:
#             if not ParserService.allowed_file(file.filename):
#                 raise BadRequest(f'Invalid file type: {file.filename}')
#
#         # Generate job ID
#         job_id = str(uuid.uuid4())
#
#         job_status = JobStatus(
#             job_id=job_id,
#             status='pending',
#             created_at=datetime.now(UTC),
#             file_count=len(files),
#             processed_count=0,
#             errors=[],
#             results=[]
#         )
#         services.redis_client.hset(
#             f'job:{job_id}',
#             mapping={
#                 'status': job_status.status,
#                 'created_at': job_status.created_at.isoformat(),
#                 'file_count': job_status.file_count,
#                 'processed_count': 0,
#                 'error_count': 0,
#                 'data': json.dumps({
#                     'file_paths': [],
#                     'errors': [],
#                     'results': []
#                 })
#             }
#         )
#
#         parent = get_cloud_tasks_queue_path(
#             current_app.config['CONFIGURATION'],
#             services.cloud_tasks_client
#         )
#         task = {
#             'http_request': {
#                 'http_method': tasks_v2.HttpMethod.POST,
#                 'url': f"{os.getenv('SERVICE_URL')}/tasks/process-pdfs",
#                 'headers': {'Content-Type': 'application/json'},
#                 'body': json.dumps({
#                     'job_id': job_id,
#                     'gcs_paths': gcs_paths
#                 }).encode()
#             }
#         }
#
#     except Exception as ex:



@invoice_bp.route('/process-pdfs', methods=['POST'])
def process_pdfs():
    """
    Process uploaded PDF invoices
    ---
    tags:
      - Invoices
    parameters:
      - in: formData
        name: pdfs
        type: file
        required: true
        description: PDF files to process
    responses:
      200:
        description: Successfully processed PDFs
      400:
        description: Invalid input
      500:
        description: Internal server error
    """
    try:
        if 'pdfs' not in request.files:
            raise BadRequest('No files provided')

        files: List[FileStorage] = request.files.getlist('pdfs')

        if not files:
            raise BadRequest('No files selected')

        # Validate files
        for file in files:
            if not ParserService.allowed_file(file.filename):
                raise BadRequest(f'Invalid file type: {file.filename}')

        # Generate job ID and process files
        job_id = uuid.uuid4().hex
        current_app.logger.info(f'Starting job {job_id} for {len(files)} files')

        processing_results = services.invoice_parser_service.parse(job_id, files)

        current_app.logger.info(f'Completed job {job_id}')

        return jsonify({
            'job_id': job_id,
            'message': f'Processed {len(files)} files',
            'results': processing_results
        }), 200

    except BadRequest as e:
        current_app.logger.warning(f'Bad request: {str(e)}')
        return jsonify({'error': str(e)}), 400

    except Exception as e:
        current_app.logger.error(f'Error processing PDFs: {str(e)}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


def event_stream(job_id):
    """Generator function for SSE"""
    last_index = 0

    while True:
        # Check job status
        job_status = services.redis_client.hget(f'job:{job_id}', 'status')

        if job_status == 'error':
            error = services.redis_client.hget(f'job:{job_id}', 'error')
            yield f"data: {json.dumps({'error': error})}\n\n"
            break

        # Get new responses
        responses = services.redis_client.lrange(f'responses:{job_id}', last_index, -1)

        for response in responses:
            yield f"data: {response}\n\n"
            last_index += 1

        if job_status == 'completed' and not responses:
            break

        # Wait before next check
        time.sleep(0.5)


@invoice_bp.route('/stream/<job_id>', methods=['GET'])
def stream(job_id):
    """SSE endpoint"""
    return Response(
        event_stream(job_id),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )


@invoice_bp.route('/status/<job_id>', methods=['GET'])
def get_status(job_id):
    """Get job status"""
    job_data = services.redis_client.hgetall(f'job:{job_id}')

    if not job_data:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(job_data)
