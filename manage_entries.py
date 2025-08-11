from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy.inspection import inspect
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Integer, Text, Boolean, Float, DateTime, Enum, func, Date, DateTime
from .models import MODELS
from . import db
from datetime import datetime
from .page_editor import markdown_to_html, slugify
import json



manage_entries = Blueprint('manage_entries', __name__)


@manage_entries.route('/manage-entry', methods=['GET'])
@login_required
def create_entry_page():
    return render_template('manage_entry.html', user=current_user)


def extract_model_fields(model_class):
    mapper = inspect(model_class)
    fields = []

    for column in mapper.columns:
        if column.name in ('id', 'created_at', 'updated_at'):
            continue

        col_type = column.type
        field = {
            'name': column.name,
            'nullable': column.nullable,
        }

        if isinstance(col_type, Enum):
            field['type'] = 'enum'
            field['choices'] = list(col_type.enums)

        elif column.foreign_keys:
            field['type'] = 'foreignkey'
            fk = list(column.foreign_keys)[0]
            ref_table = fk.column.table.name
            ref_model = next((cls for cls in MODELS.values() if getattr(cls, '__tablename__', None) == ref_table), None)

            field['ref_table'] = ref_table
            field['ref_model'] = ref_model.__name__ if ref_model else None

            if ref_model:
                field['choices'] = [{'id': item.id, 'label': str(item)} for item in ref_model.query.all()]

        else:
            field['type'] = (
                'integer' if isinstance(col_type, Integer) else
                'float' if isinstance(col_type, Float) else
                'boolean' if isinstance(col_type, Boolean) else
                'datetime' if isinstance(col_type, DateTime) else
                'textlong' if isinstance(col_type, Text) else
                'string'
            )
        fields.append(field)

    # Handle relationships (many-to-many, one-to-many, etc.)
    for rel in mapper.relationships:
        # Skip backrefs already represented by foreign key columns
        if not rel.uselist and rel.direction.name == "MANYTOONE":
            continue

        related_model = rel.mapper.class_
        field = {
            'name': rel.key,
            'type': 'relationship',
            'relationship_type': 'many' if rel.uselist else 'one',
            'ref_model': related_model.__name__,
            'choices': [{'id': item.id, 'label': str(item)} for item in related_model.query.all()]
        }
        fields.append(field)

    return fields
def extract_entry_values(model_instance):
    mapper = inspect(model_instance.__class__)
    fields = []

    for column in mapper.columns:
        if column.name in ('id', 'created_at', 'updated_at'):
            continue

        value = getattr(model_instance, column.name)
        fields.append({
            'name': column.name,
            'value': value
        })

    return fields

@manage_entries.route('/get-fields/<model_name>')
@login_required
def get_fields(model_name):
    model = MODELS.get(model_name.lower())
    if not model:
        return jsonify({'error': 'Invalid model'}), 400

    return jsonify(extract_model_fields(model))


@manage_entries.route('/get-entries/<model_name>')
@login_required
def get_entries(model_name):
    model = MODELS.get(model_name.lower())
    if not model:
        return jsonify({'error': 'Invalid model'}), 400

    entries = model.query.all()
    return jsonify([{'id': e.id, 'label': str(e)} for e in entries])


@manage_entries.route('/get-entry/<model_name>/<int:entry_id>')
@login_required
def get_entry(model_name, entry_id):
    model = MODELS.get(model_name.lower())
    if not model:
        return jsonify({'error': 'Invalid model'}), 400

    entry = model.query.get_or_404(entry_id)
    mapper = inspect(model)

    data = {
        col.name: getattr(entry, col.name)
        for col in inspect(model).columns
        if col.name not in ('id', 'created_at', 'updated_at')
    }

    for rel in mapper.relationships:
        value = getattr(entry, rel.key)

        if rel.uselist:  # list of related objects
            data[rel.key] = [
                {"id": r.id, "name": str(r)} for r in value
            ]
        else:  # single related object
            data[rel.key] = {"id": value.id, "name": str(value)} if value else None
    return jsonify(data)

#removed because it is unneceseary but useful for key reorder bug
@manage_entries.route('/get-entry-by-name/<model_name>/<path:name>')
@login_required
def get_entry_by_name(model_name, name):
    model = MODELS.get(model_name.lower())
    if not model:
        return jsonify({"error": "Invalid model"}), 400

    mapper = inspect(model)
    columns = {col.name: col for col in mapper.columns}

    if 'slug' in columns:
        column = columns['slug']
        search_value = slugify(name)
    elif hasattr(model, "name"):
        column = getattr(model, "name")
        search_value = slugify(name)
    elif hasattr(model, "title"):
        column = getattr(model, "title")
        search_value = slugify(name)
    else:
        return jsonify({"error": "No searchable field"}), 400

    entry = model.query.filter(func.lower(column) == search_value).first()

    if not entry:
        return jsonify({"error": "Not found"}), 404

    data = {
        col.name: getattr(entry, col.name)
        for col in columns.values()
        if col.name not in ('id', 'created_at', 'updated_at')
    }
    for rel in mapper.relationships:
        value = getattr(entry, rel.key)

        if rel.uselist:  # list of related objects
            data[rel.key] = [
                {"id": r.id, "name": str(r)} for r in value
            ]
        else:  # single related object
            data[rel.key] = {"id": value.id, "name": str(value)} if value else None
    return jsonify(data)

@manage_entries.route('/submit-page', methods=['POST'])
@login_required
def submit_page():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    if data.get("parent_id") == "":
        data["parent_id"] = None
    page_type = data.get('page_type')
    model_class = MODELS.get(page_type)

    if not model_class:
        return jsonify({'error': 'Invalid page type'}), 400

    mapper = inspect(model_class)
    relationships = {rel.key: rel for rel in mapper.relationships}
    allowed_fields = [col.name for col in mapper.columns if col.name not in ('id', 'created_at', 'updated_at')]
    columns = {col.key: col for col in mapper.columns}

    rel_data = {}
    clean_data = {}
    # Separate normal columns and relationships
    for key, raw_value in data.items():
        if key in allowed_fields:
            value = None if raw_value == '' else raw_value

            column = mapper.columns.get(key)
            if isinstance(column.type, db.DateTime) and value is not None:
                try:
                    value = datetime.fromisoformat(value)
                except ValueError:
                    return redirect(url_for('create_pages.create_page'))

            clean_data[key] = value

        elif key in relationships:
            rel = relationships[key]
            if rel.uselist:  # many-to-many or one-to-many
                # Handle empty
                if raw_value in (None, "", []):
                    rel_data[key] = []
                else:
                    # If string, try parsing JSON or wrap in list
                    if isinstance(raw_value, str):
                        try:
                            parsed = json.loads(raw_value)
                            if isinstance(parsed, list):
                                raw_value = parsed
                            else:
                                raw_value = [parsed]
                        except Exception:
                            raw_value = [raw_value]
        
                    # Ensure list type
                    if not isinstance(raw_value, list):
                        raw_value = [raw_value]
        
                    # Coerce all to int if possible
                    try:
                        raw_value = [int(v) for v in raw_value if v not in (None, "")]
                    except ValueError:
                        return jsonify({'error': f"'{key}' contains invalid IDs"}), 400
        
                    rel_data[key] = raw_value
        
            else:  # single relationship
                if raw_value in (None, ""):
                    rel_data[key] = None
                else:
                    try:
                        rel_data[key] = int(raw_value)
                    except ValueError:
                        return jsonify({'error': f"'{key}' must be an integer ID"}), 400
    if page_type == "page" and clean_data.get("content_md"):
        clean_data["content"] = markdown_to_html(clean_data["content_md"])
    
    id = data.get('id')
    try:
        if id:
            instance = model_class.query.get(id)
            if not instance:
                return jsonify({'error': 'Entry not found.'}), 404

            for key, val in clean_data.items():
                setattr(instance, key, val)

        else:
            instance = model_class(**clean_data)
            db.session.add(instance)

        # Handle relationship assignments
        for key, ids in rel_data.items():
            rel = relationships[key]
            related_model = rel.mapper.class_

            if rel.uselist:
                related_objects = related_model.query.filter(
                    related_model.id.in_(ids)
                ).all()
                setattr(instance, key, related_objects)
            else:
                if ids is None:
                    setattr(instance, key, None)
                else:
                    related_object = related_model.query.get(ids)
                    setattr(instance, key, related_object)

        db.session.commit()
        return jsonify({
            'success': True,
            'message': f'{page_type.capitalize()} saved!',
            'id': instance.id,
            'slug': getattr(instance, 'slug', None)
        })
    except IntegrityError as e:
        db.session.rollback()
        if 'UNIQUE constraint failed' in str(e.orig):
            return jsonify({'error': 'An entry with that name already exists. Please choose a different name.'}), 400
        return jsonify({'error': 'Database error occurred.'}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@manage_entries.route('/edit-entry/<model_name>/<int:entry_id>', methods=['POST'])
@login_required
def edit_entry(model_name, entry_id):
    model = MODELS.get(model_name.lower())
    if not model:
        return jsonify({'error': 'Invalid model'}), 400

    entry = model.query.get_or_404(entry_id)
    data = request.get_json()
    if data.get("parent_id") == "":
        data["parent_id"] = None
    if model_name.lower() == "page" and data.get("content_md"):
        data["content"] = markdown_to_html(data["content_md"])
    try:
        mapper = inspect(model)
        relationships = {rel.key: rel for rel in mapper.relationships}
        columns = {col.key: col for col in mapper.columns}
        for key, value in data.items():
            if key in relationships:  # Handle relationship
                rel = relationships[key]
                related_model = rel.mapper.class_
                if rel.uselist:  # many-to-many or one-to-many
                    if value is None or value == "":
                        value = []
                    elif isinstance(value, str):
                        try:
                            value = json.loads(value)
                        except Exception:
                            value = [value]

                    elif not isinstance(value, list):
                        return jsonify({'error': f"'{key}' must be a list of IDs"}), 400

                    # Convert IDs to int and filter valid integers
                    try:
                        if isinstance(value, (int, str)):
                            value = [value]
                        ids = list(map(int, value))
                    except Exception:
                        return jsonify({'error': f"Invalid IDs provided for '{key}'"}), 400

                    # Query related model for the list of IDs
                    related_model = rel.mapper.class_
                    related_objs = related_model.query.filter(related_model.id.in_(ids)).all()

                    # Assign the list of related objects to the relationship attribute
                    setattr(entry, key, related_objs)
                else:  # many-to-one or one-to-one
                    if value is None:
                        setattr(entry, key, None)
                    else:
                        related_object = related_model.query.get(value)
                        setattr(entry, key, related_object)
            elif hasattr(entry, key):
                if key in columns:
                            col_type = columns[key].type
                            if isinstance(value, str):
                                if isinstance(col_type, DateTime):
                                    try:
                                        value = datetime.fromisoformat(value)
                                    except ValueError:
                                        return jsonify({'error': f"Invalid datetime format for '{key}'"}), 400
                                    
                                elif isinstance(col_type, Date):
                                    try:
                                        value = datetime.fromisoformat(value).date()
                                    except ValueError:
                                        return jsonify({'error': f"Invalid date format for '{key}'"}), 400
                setattr(entry, key, value)
        db.session.commit()
        return jsonify({'success': True, 'slug': getattr(entry, 'slug', None)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@manage_entries.route('/delete-entry/<model>/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_entry(model, entry_id):
    model_class = MODELS.get(model)
    if not model_class:
        return jsonify({'error': 'Invalid model type'}), 400

    instance = db.session.get(model_class, entry_id)
    if not instance:
        return jsonify({'error': 'Entry not found'}), 404

    try:
        db.session.delete(instance)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
