from datetime import datetime
from collections import Counter
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .exts import db
from .models import Goal, Transaction

index = Blueprint("index", __name__)

def build_past_goals_data(user_id):
    """Helper to structure past goals with statistics for both index and past_goals pages"""
    past_goals = Goal.query.filter_by(user_id=user_id, completed=True).order_by(Goal.completed_at.desc()).all()
    past_goals_data = []
    for g in past_goals:
        g_txs = Transaction.query.filter_by(goal_id=g.id).order_by(Transaction.created_at.desc()).all()
        g_saves = [t for t in g_txs if t.tx_type == "save"]
        
        top_tag = Counter([t.tag for t in g_saves if t.tag]).most_common(1)
        top_tag_name = top_tag[0][0] if top_tag else "#SpiteSave"
        top_tag_sum = sum(t.amount for t in g_saves if t.tag == top_tag_name)
        duration_days = max(1, ((g.completed_at or datetime.utcnow()) - g.created_at).days + 1)
        
        past_goals_data.append({
            "goal": g,
            "transactions": g_txs,
            "top_tag": top_tag_name,
            "top_tag_sum": top_tag_sum,
            "duration_days": duration_days,
            "saves_count": len(g_saves)
        })
    return past_goals_data

@index.route("/", methods=["GET"])
@login_required
def index_page():
    # 1. Look for an active, incomplete goal
    active_goal = Goal.query.filter_by(user_id=current_user.id, completed=False).first()

    # 2. If no incomplete goal, check if there is a recently completed goal awaiting reset
    if not active_goal:
        latest_goal = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.id.desc()).first()
        if latest_goal and latest_goal.completed:
            active_goal = latest_goal
        else:
            # First time user with 0 goals created
            return render_template("no_goal.html", user=current_user, progress_pct=0)

    # 3. Fetch transactions for the active goal
    transactions = Transaction.query.filter_by(
        user_id=current_user.id, goal_id=active_goal.id
    ).order_by(Transaction.created_at.desc()).all()

    # 4. Build properly formatted past goals data (solves the 'no attribute goal' crash)
    past_goals_data = build_past_goals_data(current_user.id)
    
    # 5. Calculate lifetime savings
    all_saves = Transaction.query.filter_by(user_id=current_user.id, tx_type="save").all()
    lifetime_saved = sum(t.amount for t in all_saves)

    progress_pct = min(100, round((active_goal.current_amount / active_goal.target_amount) * 100, 1)) if active_goal.target_amount > 0 else 0

    return render_template(
        "index.html",
        user=current_user,
        goal=active_goal,
        progress_pct=progress_pct,
        transactions=transactions,
        past_goals_data=past_goals_data,
        lifetime_saved=lifetime_saved
    )

@index.route("/goal/add", methods=["POST"])
@login_required
def add_goal():
    title = request.form.get("title", "New Goal").strip()
    target_amount = request.form.get("target_amount", 5000.0, type=float)

    new_goal = Goal(
        user_id=current_user.id,
        title=title,
        target_amount=max(100.0, target_amount),
        current_amount=0.0,
        completed=False
    )
    db.session.add(new_goal)
    db.session.commit()
    return redirect(url_for("index.index_page"))

@index.route("/transaction/add", methods=["POST"])
@login_required
def add_transaction():
    goal_id = request.form.get("goal_id", type=int)
    tx_type = request.form.get("tx_type", "save")
    amount = request.form.get("amount", type=float)
    description = request.form.get("description", "").strip()
    tag = request.form.get("tag", "#SpiteSave").strip()

    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()

    # --- LOCK TRANSACTION CHECK ---
    if goal.completed or goal.current_amount >= goal.target_amount:
        flash("Goal reached! Claim this goal and start a new one to log more transactions.", "error")
        return redirect(url_for("index.index_page"))
    # -----------------------------

    if not amount or amount <= 0 or not description:
        flash("Please enter a valid amount and description.", "error")
        return redirect(url_for("index.index_page"))

    was_below_target = goal.current_amount < goal.target_amount

    if tx_type == "save":
        goal.current_amount += amount
    else:
        goal.current_amount = max(0.0, goal.current_amount - amount)

    hit_milestone = False
    if was_below_target and goal.current_amount >= goal.target_amount:
        hit_milestone = True
        goal.completed = True
        goal.completed_at = datetime.utcnow()

    tx = Transaction(
        user_id=current_user.id,
        goal_id=goal.id,
        tx_type=tx_type,
        amount=amount,
        description=description,
        tag=tag,
        is_milestone=hit_milestone
    )
    db.session.add(tx)
    db.session.commit()

    return redirect(url_for("index.index_page", celebrated="1" if hit_milestone else None))
@index.route("/transaction/delete/<int:tx_id>", methods=["POST"])
@login_required
def delete_transaction(tx_id):
    tx = Transaction.query.filter_by(id=tx_id, user_id=current_user.id).first_or_404()
    goal = Goal.query.get(tx.goal_id)
    if goal:
        if tx.tx_type == "save":
            goal.current_amount = max(0.0, goal.current_amount - tx.amount)
        else:
            goal.current_amount += tx.amount

        if goal.current_amount < goal.target_amount:
            goal.completed = False
            goal.completed_at = None

    db.session.delete(tx)
    db.session.commit()
    return redirect(url_for("index.index_page"))

@index.route("/goal/edit", methods=["POST"])
@login_required
def edit_goal():
    goal_id = request.form.get("goal_id", type=int)
    title = request.form.get("title", "").strip()
    target_amount = request.form.get("target_amount", type=float)

    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    if title and target_amount and target_amount > 0:
        goal.title = title
        goal.target_amount = target_amount
        if goal.current_amount >= goal.target_amount:
            goal.completed = True
            goal.completed_at = goal.completed_at or datetime.utcnow()
        else:
            goal.completed = False
            goal.completed_at = None
        db.session.commit()
    return redirect(url_for("index.index_page"))

@index.route("/goal/new", methods=["POST"])
@login_required
def start_new_goal():
    old_goal_id = request.form.get("old_goal_id", type=int)
    title = request.form.get("title", "Next Target").strip()
    target_amount = request.form.get("target_amount", 5000.0, type=float)
    rollover = request.form.get("rollover") == "on"

    old_goal = Goal.query.filter_by(id=old_goal_id, user_id=current_user.id).first()
    starting_balance = 0.0

    if old_goal:
        old_goal.completed = True
        old_goal.completed_at = old_goal.completed_at or datetime.utcnow()
        if rollover and old_goal.current_amount > old_goal.target_amount:
            starting_balance = old_goal.current_amount - old_goal.target_amount

    new_goal = Goal(
        user_id=current_user.id,
        title=title,
        target_amount=max(100.0, target_amount),
        current_amount=starting_balance,
        completed=False
    )
    db.session.add(new_goal)
    db.session.commit()

    if starting_balance > 0:
        rollover_tx = Transaction(
            user_id=current_user.id,
            goal_id=new_goal.id,
            tx_type="save",
            amount=starting_balance,
            description=f"Surplus rolled over from '{old_goal.title}'",
            tag="#Rollover"
        )
        db.session.add(rollover_tx)
        db.session.commit()

    return redirect(url_for("index.index_page"))

@index.route("/past-goals", methods=["GET"])
@login_required
def past_goals_page():
    past_goals_data = build_past_goals_data(current_user.id)
    all_saves = Transaction.query.filter_by(user_id=current_user.id, tx_type="save").all()
    lifetime_saved = sum(t.amount for t in all_saves)

    return render_template(
        "past_goals.html",
        user=current_user,
        past_goals_data=past_goals_data,
        lifetime_saved=lifetime_saved
    )
