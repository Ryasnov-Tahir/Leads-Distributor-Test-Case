from app import models
import random


def get_operator(db, operator_id):
    return db.query(models.Operator).filter(models.Operator.id == operator_id).first()


def create_operator(db, oper):
    db_oper = models.Operator(name=oper.name, active=oper.active, limit=oper.limit)
    db.add(db_oper)
    db.commit()
    db.refresh(db_oper)
    return db_oper


def list_operators(db):
    return db.query(models.Operator).all()


def update_operator(db, operator_id, active=None, limit=None):
    oper = get_operator(db, operator_id)
    if not oper:
        return None
    if active is not None:
        oper.active = active
    if limit is not None:
        oper.limit = limit
    db.commit()
    db.refresh(oper)
    return oper


def create_source(db, source_create):
    source = models.Source(name=source_create.name)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def assign_operator_to_source(db, source_id, assign):
    oper = get_operator(db, assign.operator_id)
    source = db.query(models.Source).filter(models.Source.id == source_id).first()
    if not oper or not source:
        return None
    source_oper = (
        db.query(models.SourceOperator)
        .filter_by(source_id=source_id, operator_id=assign.operator_id)
        .first()
    )
    if source_oper:
        source_oper.weight = assign.weight
    else:
        source_oper = models.SourceOperator(
            source_id=source_id, operator_id=assign.operator_id, weight=assign.weight
        )
        db.add(source_oper)
    db.commit()
    db.refresh(source_oper)
    return source_oper


def find_or_create_lead(db, external_id=None, e_mail=None):
    query = db.query(models.Lead)
    if external_id:
        lead = query.filter(models.Lead.external_id == external_id).first()
        if lead:
            return lead
    if e_mail:
        lead = query.filter(models.Lead.e_mail == e_mail).first()
        if lead:
            return lead
    lead = models.Lead(external_id=external_id, e_mail=e_mail)
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


def count_active_contacts_for_operator(db, operator_id):
    return (
        db.query(models.Contact)
        .filter(
            models.Contact.operator_id == operator_id,
            models.Contact.status == models.ContactStatus.open,
        )
        .count()
    )


def available_operators_for_source(db, source_id):
    rows = (
        db.query(models.SourceOperator)
        .filter(models.SourceOperator.source_id == source_id)
        .all()
    )
    result = []
    for source_oper in rows:
        oper = source_oper.operator
        if not oper.active:
            continue
        current_load = count_active_contacts_for_operator(db, oper.id)
        if oper.limit is not None and current_load >= oper.limit:
            continue
        result.append((oper, source_oper.weight))
    return result


def choose_operator_by_weight(candidates):
    """Пока реализовал через random, что-то поинтереснее придумать не успел"""
    if not candidates:
        return None
    total = sum(i_weight for _, i_weight in candidates)
    rand = random.uniform(0, total)
    upto = 0
    for i_oper, i_wight in candidates:
        if upto + i_wight >= rand:
            return i_oper
        upto += i_wight
    return candidates[-1][0]


def create_contact(db, contact):
    lead = find_or_create_lead(
        db, external_id=contact.external_id, e_mail=contact.e_mail
    )
    candidates = available_operators_for_source(db, contact.source_id)
    chosen = choose_operator_by_weight(candidates)
    operator_id = chosen.id if chosen else None
    contact = models.Contact(
        lead_id=lead.id,
        source_id=contact.source_id,
        operator_id=operator_id,
        payload=contact.payload,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def list_leads(db):
    return db.query(models.Lead).all()


def stats(db):
    oper_list = db.query(models.Operator).all()
    sources = db.query(models.Source).all()
    oper_stats = []
    for i_oper in oper_list:
        total = (
            db.query(models.Contact)
            .filter(models.Contact.operator_id == i_oper.id)
            .count()
        )
        open_cnt = (
            db.query(models.Contact)
            .filter(
                models.Contact.operator_id == i_oper.id,
                models.Contact.status == models.ContactStatus.open,
            )
            .count()
        )
        oper_stats.append(
            {
                "operator_id": i_oper.id,
                "name": i_oper.name,
                "total": total,
                "open": open_cnt,
            }
        )
    source_stats = []
    for i_source in sources:
        total = (
            db.query(models.Contact)
            .filter(models.Contact.source_id == i_source.id)
            .count()
        )
        source_stats.append(
            {"source_id": i_source.id, "name": i_source.name, "total": total}
        )
    return {"operators": oper_stats, "sources": source_stats}
